<script lang="ts">
  let { lyrics = '', fontSize = 1.2 }: { lyrics?: string; fontSize?: number } = $props();

  const SECTION_TAGS = new Set([
    'verse', 'chorus', 'bridge', 'intro', 'outro', 'pre-chorus', 'tag',
    'interlude', 'instrumental', 'break', 'solo', 'coda', 'refrain', 'hook',
    'riff', 'build', 'drop', 'climax', 'ending', 'transition'
  ]);

  interface Segment {
    type: 'text' | 'bold' | 'italic' | 'superscript' | 'instrument' | 'colored';
    text: string;
    color?: string;
  }

  interface Line {
    type: 'section-header' | 'content';
    text: string;
    sectionName?: string;
    segments?: Segment[];
  }

  function parseInline(text: string): Segment[] {
    const segments: Segment[] = [];
    const regex = /(\*\*(.+?)\*\*)|(\*(.+?)\*)|(\^(.+?)\^)|\[([a-z-]+)\]|\{color:([^}]+)\}(.+?)\{\/color\}|(\\.)/g;
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    const instrumentSet = new Set(['solo', 'guitar', 'drums', 'keys', 'bass', 'vocal', 'synth', 'pad']);

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        segments.push({ type: 'text', text: text.slice(lastIndex, match.index) });
      }

      if (match[2]) {
        segments.push({ type: 'bold', text: match[2] });
      } else if (match[4]) {
        segments.push({ type: 'italic', text: match[4] });
      } else if (match[6]) {
        segments.push({ type: 'superscript', text: match[6] });
      } else if (match[7]) {
        const tag = match[7].toLowerCase();
        if (instrumentSet.has(tag)) {
          segments.push({ type: 'instrument', text: tag });
        } else {
          segments.push({ type: 'text', text: `[${match[7]}]` });
        }
      } else if (match[8] && match[9] && match[10]) {
        segments.push({ type: 'colored', text: match[10], color: match[9] });
      } else if (match[11]) {
        segments.push({ type: 'text', text: match[11].slice(1) });
      }

      lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
      segments.push({ type: 'text', text: text.slice(lastIndex) });
    }

    return segments;
  }

  function parseLyrics(text: string): Line[] {
    const lines = text.split('\n');
    const result: Line[] = [];

    for (const raw of lines) {
      const trimmed = raw.trim();
      const match = trimmed.match(/^\[(.+)\]$/);
      if (match) {
        const section = match[1].toLowerCase();
        const isSection = SECTION_TAGS.has(section) || SECTION_TAGS.has(section.replace(/\d+\s*$/, '').trim());
        if (isSection) {
          result.push({ type: 'section-header', text: match[1], sectionName: match[1] });
          continue;
        }
      }
      result.push({ type: 'content', text: raw, segments: parseInline(raw) });
    }

    return result;
  }

  let lines = $derived(parseLyrics(lyrics));

  function sectionColor(name: string): string {
    const n = name.toLowerCase().replace(/\d+\s*$/, '').trim();
    const colors: Record<string, string> = {
      'verse': 'var(--accent)',
      'chorus': '#f59e0b',
      'refrain': '#f59e0b',
      'hook': '#f59e0b',
      'bridge': '#8b5cf6',
      'pre-chorus': '#06b6d4',
      'intro': '#10b981',
      'outro': '#ef4444',
      'ending': '#ef4444',
      'tag': '#ec4899',
      'interlude': '#6b7280',
      'instrumental': '#6b7280',
      'break': '#6b7280',
      'solo': '#f97316',
      'build': '#8b5cf6',
      'drop': '#06b6d4',
      'transition': '#6b7280',
    };
    return colors[n] || 'var(--accent)';
  }

  function instrumentIcon(name: string): string {
    const icons: Record<string, string> = {
      'solo': '🎸',
      'guitar': '🎸',
      'drums': '🥁',
      'keys': '🎹',
      'bass': '🎸',
      'vocal': '🎤',
      'synth': '🎹',
      'pad': '🎹',
    };
    return icons[name] || '🎵';
  }
</script>

<div class="lyrics-renderer" style="font-size: {fontSize}rem">
  {#each lines as line}
    {#if line.type === 'section-header'}
      <div class="section-header" style="--section-color: {sectionColor(line.text)}">
        {line.text}
      </div>
    {:else if line.segments && line.segments.length > 0}
      <div class="lyrics-line">
        {#each line.segments as seg}
          {#if seg.type === 'text'}
            <span>{seg.text}</span>
          {:else if seg.type === 'bold'}
            <strong>{seg.text}</strong>
          {:else if seg.type === 'italic'}
            <em>{seg.text}</em>
          {:else if seg.type === 'superscript'}
            <sup>{seg.text}</sup>
          {:else if seg.type === 'instrument'}
            <span class="instrument-badge" title={seg.text}>
              {instrumentIcon(seg.text)} {seg.text}
            </span>
          {:else if seg.type === 'colored'}
            <span class="colored-text" style="color:{seg.color}">{seg.text}</span>
          {/if}
        {/each}
      </div>
    {:else}
      <div class="lyrics-line"><br /></div>
    {/if}
  {/each}
</div>

<style>
  .lyrics-renderer {
    font-family: 'DM Mono', monospace;
    white-space: pre-wrap;
    line-height: 1.9;
    color: var(--lyrics-text);
  }

  .section-header {
    display: inline-block;
    padding: 0.2rem 0.75rem;
    margin: 0.75rem 0 0.5rem 0;
    border-radius: 6px;
    font-size: 0.85em;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    background: color-mix(in srgb, var(--section-color) 20%, transparent);
    color: var(--section-color);
    border: 1px solid color-mix(in srgb, var(--section-color) 35%, transparent);
  }

  .lyrics-line {
    min-height: 1.9em;
  }

  sup {
    font-size: 0.7em;
    vertical-align: super;
    color: var(--accent);
    font-weight: 600;
  }

  .instrument-badge {
    display: inline-block;
    padding: 0.04rem 0.45rem;
    margin: 0 0.1rem;
    border-radius: 4px;
    font-size: 0.75em;
    font-weight: 600;
    background: var(--bg3);
    border: 1px solid var(--border2);
    color: var(--text2);
    vertical-align: middle;
  }

  strong { font-weight: 700; }
  em { font-style: italic; }
</style>
