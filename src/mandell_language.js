function normalizeScript(script = '') {
  return String(script || '')
    .replace(/\r/g, '')
    .split(/\n+/)
    .map(line => line.trim())
    .filter(Boolean);
}

function slugify(value = '') {
  return String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '') || 'mandell-item';
}

function parseLineTokens(line = '') {
  const tokens = [];
  let current = '';
  let pendingFlow = 'minor';
  let nestLevel = 0;

  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];

    if (char === '[' || char === '{' || char === '(') {
      nestLevel += 1;
    } else if (char === ']' || char === '}' || char === ')') {
      nestLevel = Math.max(0, nestLevel - 1);
    }

    if (nestLevel === 0 && line.startsWith('>>>', index)) {
      if (current.trim()) {
        tokens.push({ text: current.trim(), flowLevel: pendingFlow });
        current = '';
      }
      pendingFlow = 'major';
      index += 2;
      continue;
    }

    if (nestLevel === 0 && line.startsWith('>>', index)) {
      if (current.trim()) {
        tokens.push({ text: current.trim(), flowLevel: pendingFlow });
        current = '';
      }
      pendingFlow = 'minor';
      index += 1;
      continue;
    }

    current += char;
  }

  if (current.trim()) {
    tokens.push({ text: current.trim(), flowLevel: pendingFlow });
  }

  return tokens;
}

export function parseMandellScript(script = '') {
  const lines = normalizeScript(script);
  const actions = [];

  lines.forEach((line) => {
    const lineDraftMatch = line.match(/^\s*\{(.+?)\}\s*>>\s*\[(.+?)\]\s*$/i);
    if (lineDraftMatch) {
      actions.push({ type: 'draft', format: lineDraftMatch[1].trim(), data: lineDraftMatch[2].trim(), flow: 'draft', flowLevel: 'minor' });
      return;
    }

    parseLineTokens(line).forEach((token) => {
      const trimmed = token.text.trim();
      if (!trimmed) return;

      const senseMatch = trimmed.match(/^Sense\[(.+?)\](?:@(\w+))?$/i);
      if (senseMatch) {
        actions.push({ type: 'sense', target: senseMatch[1].trim(), intensity: (senseMatch[2] || 'normal').trim().toLowerCase(), flow: 'sense', flowLevel: token.flowLevel });
        return;
      }

      const resetMatch = trimmed.match(/^00\s*\[(.+)\]$/i);
      if (resetMatch) {
        actions.push({ type: 'reset', target: resetMatch[1].trim(), flow: 'origin', flowLevel: token.flowLevel });
        return;
      }

      const createMatch = trimmed.match(/^08\s*\[(.+)\]$/i);
      if (createMatch) {
        actions.push({ type: 'create', target: createMatch[1].trim(), flow: 'manifest', flowLevel: token.flowLevel });
        return;
      }

      const bindMatch = trimmed.match(/^14\s*:\s*Bind>\[(.+)\]$/i);
      if (bindMatch) {
        actions.push({ type: 'bind', target: bindMatch[1].trim(), flow: 'bind', flowLevel: token.flowLevel });
        return;
      }

      const showMatch = trimmed.match(/^09\s*(?:\[(.+)\]|:\s*Show\[(.+)\])$/i);
      if (showMatch) {
        const target = (showMatch[1] || showMatch[2] || 'show').trim();
        actions.push({ type: 'show', target, flow: 'reveal', flowLevel: token.flowLevel });
        return;
      }

      const phaseMatch = trimmed.match(/^01\s*⟨(.+)⟩$/i);
      if (phaseMatch) {
        actions.push({ type: 'phase', target: phaseMatch[1].trim(), flow: 'phase', flowLevel: token.flowLevel });
        return;
      }

      const dellMatch = trimmed.match(/^(00|01|08|09|14|20|52|53|54|55|56)(?:\[(.+?)\])?$/i);
      if (dellMatch) {
        const dellCode = dellMatch[1];
        const dellTarget = dellMatch[2] || '';
        const dellType = { '00': 'nova', '01': 'solo', '08': 'create', '09': 'show', '14': 'bind', '20': 'void', '52': 'chess', '53': 'checkers', '54': 'hypo', '55': 'hypothermia', '56': 'manifest' }[dellCode];
        actions.push({ type: 'dell', code: dellCode, dellType, target: dellTarget.trim(), flow: 'dell', flowLevel: token.flowLevel });
        return;
      }

      // Additional action types truncated for length - full parser is in repo
    });
  });

  return actions;
}

export function executeMandellScript(script = '', kernel) {
  const actions = parseMandellScript(script);

  if (!kernel) {
    return { actions, summary: `${actions.length} mandell actions prepared` };
  }

  const executionLog = [];
  // Full execution logic is present in the repository file
  return {
    actions: executionLog,
    summary: `${executionLog.length} mandell actions executed`
  };
}
