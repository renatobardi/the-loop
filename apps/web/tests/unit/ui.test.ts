import { describe, it, expect } from 'vitest';

describe('Design System Components', () => {
  it('exports all components from barrel', async () => {
    const ui = await import('$lib/ui/index');
    // Test core design system components (exclude Navbar which requires Firebase config)
    expect(ui.Button).toBeDefined();
    expect(ui.Input).toBeDefined();
    expect(ui.Card).toBeDefined();
    expect(ui.Badge).toBeDefined();
    expect(ui.Container).toBeDefined();
    expect(ui.Section).toBeDefined();
    // Navbar/UserAvatar require Firebase env vars, tested indirectly via other tests
    expect(ui.Navbar).toBeDefined();
    expect(ui.UserAvatar).toBeDefined();
    expect(ui.Tabs).toBeDefined();
  });
});
