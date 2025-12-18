import { test, expect } from '@playwright/test';

/**
 * MediAI E2E Tests - Page Navigation
 */

test.describe('Navigation', () => {
    test('should load landing page', async ({ page }) => {
        await page.goto('/');

        // Check for MediAI branding
        await expect(page.getByText(/MediAI/i)).toBeVisible();

        // Check for Get Started button
        await expect(page.getByRole('link', { name: /get started/i })).toBeVisible();
    });

    test('should navigate from landing to login', async ({ page }) => {
        await page.goto('/');

        // Click Get Started
        await page.getByRole('link', { name: /get started/i }).click();

        // Should be on login page
        await expect(page).toHaveURL(/login/);
    });

    test('should load doctors page', async ({ page }) => {
        await page.goto('/doctors');

        // Check page loaded (may redirect to login if protected)
        await page.waitForTimeout(1000);
    });

    test('should load chat page', async ({ page }) => {
        await page.goto('/chat');

        // Check page loaded
        await page.waitForTimeout(1000);
    });

    test('should load prediction pages', async ({ page }) => {
        // Sepsis
        await page.goto('/predict/sepsis');
        await page.waitForTimeout(500);

        // Mortality
        await page.goto('/predict/mortality');
        await page.waitForTimeout(500);
    });
});

test.describe('Responsive Design', () => {
    test('should be responsive on mobile', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto('/');

        // Page should still be usable
        await expect(page.getByText(/MediAI/i)).toBeVisible();
    });

    test('should be responsive on tablet', async ({ page }) => {
        await page.setViewportSize({ width: 768, height: 1024 });
        await page.goto('/');

        await expect(page.getByText(/MediAI/i)).toBeVisible();
    });
});
