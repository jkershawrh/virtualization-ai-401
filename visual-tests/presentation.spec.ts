import { expect, test } from '@playwright/test'

test('opening and architecture remain visually stable', async ({ page }) => {
  test.skip(Boolean(process.env.CI), 'macOS pixel baselines are verified locally; CI runs platform-neutral browser checks')
  await page.goto('/')
  await expect(page).toHaveScreenshot('opening.png', { fullPage: true })
  await page.goto('/?act=1&scene=0')
  await expect(page).toHaveScreenshot('architecture.png', { fullPage: true })
})

test('live journey opens as a workload workspace with topology on demand', async ({ page }) => {
  test.skip(Boolean(process.env.CI), 'macOS pixel baselines are verified locally; CI runs platform-neutral browser checks')
  await page.goto('/?act=4&scene=0')
  await expect(page).toHaveScreenshot('live-journey.png', { fullPage: true })
})

test('core controls are keyboard reachable', async ({ page }) => {
  await page.goto('/?act=0&scene=0')
  await page.keyboard.press('Tab')
  await expect(page.getByRole('button', { name: 'Restart presentation' })).toBeFocused()
})

test('all seven stage scenes require no vertical scroll', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'stage-1080p')
  for (const url of ['/?act=0&scene=0', '/?act=1&scene=0', '/?act=2&scene=0', '/?act=3&scene=0', '/?act=4&scene=0', '/?act=5&scene=0', '/?act=6&scene=0']) {
    await page.goto(url)
    const sizes = await page.evaluate(() => {
      const stage = document.querySelector('.stage') as HTMLElement
      return { client: stage.clientHeight, content: stage.scrollHeight, bodyOverflow: getComputedStyle(document.body).overflowY }
    })
    expect(sizes.bodyOverflow, `${url} allowed document scrolling`).toBe('hidden')
    expect(sizes.content, `${url} clipped content inside the stage`).toBeLessThanOrEqual(sizes.client + 1)
  }
})
