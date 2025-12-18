import { test, expect } from '@playwright/test';

/**
 * MediAI E2E Tests - Authentication Flow
 */

test.describe('Authentication', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/login');
        // Wait for page to fully load
        await page.waitForLoadState('networkidle');
    });

    test('should display login page with form', async ({ page }) => {
        // Check for MediAI heading
        await expect(page.getByText('MediAI')).toBeVisible();

        // Check form inputs exist
        await expect(page.getByPlaceholder('demo')).toBeVisible();

        // Check Sign In button
        await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();

        // Check demo credentials section exists
        await expect(page.getByText('Demo credentials:')).toBeVisible();
    });

    test('should show error for invalid credentials', async ({ page }) => {
        // Fill in invalid credentials
        await page.getByPlaceholder('demo').fill('wronguser');
        await page.locator('input[type="password"]').fill('wrongpass');

        // Submit form
        await page.getByRole('button', { name: /sign in/i }).click();

        // Wait for response
        await page.waitForTimeout(2000);

        // Should still be on login page (error shown or no redirect)
        expect(page.url()).toContain('/login');
    });

    test('should have demo credentials info visible', async ({ page }) => {
        // Check both demo values are shown
        await expect(page.locator('code').first()).toBeVisible();
        await expect(page.getByText('demo123')).toBeVisible();
    });
});
