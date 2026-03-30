import { describe, it, expect } from 'vitest';

describe('Design System Components', () => {
  it('exports all components from barrel', async () => {
    const ui = await import('$lib/ui/index');
    expect(ui.Button).toBeDefined();
    expect(ui.Input).toBeDefined();
    expect(ui.Card).toBeDefined();
    expect(ui.Badge).toBeDefined();
    expect(ui.Container).toBeDefined();
    expect(ui.Section).toBeDefined();
  });
});
