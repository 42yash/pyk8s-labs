// e2e/tests/main.spec.js
const { test, expect } = require('@playwright/test');

test('Full user journey: register, create cluster, run command, and delete', async ({ page }) => {
    const uniqueId = new Date().getTime();
    const userEmail = `user-${uniqueId}@example.com`;
    const clusterName = `test-cluster-${uniqueId}`;

    // 1. Registration
    await page.goto('/register');
    await expect(page).toHaveTitle(/PyK8s-Lab/);
    await page.getByPlaceholder('Enter your email address').fill(userEmail);
    await page.getByPlaceholder('Create a strong password').fill('password123');
    await page.getByPlaceholder('Confirm your password').fill('password123');
    await page.getByLabel(/I agree to use PyK8s-Lab/).check();
    await page.getByRole('button', { name: 'Create Account' }).click();

    // 2. Login
    await expect(page).toHaveURL('/login?registered=true');
    await expect(page.getByText('Registration successful!')).toBeVisible();
    await page.getByPlaceholder('Enter your email address').fill(userEmail);
    await page.getByPlaceholder('Enter your password').fill('password123');
    await page.getByRole('button', { name: 'Sign in' }).click();

    // 3. Dashboard and Cluster Creation
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText(`Welcome, ${userEmail}`)).toBeVisible();
    await page.getByPlaceholder('my-test-cluster').fill(clusterName);
    await page.getByRole('button', { name: 'Create Cluster' }).click();
    await expect(page.getByText(`Cluster "${clusterName}" is being provisioned.`)).toBeVisible();

    // 4. Wait for Cluster to be Running (SSE validation)
    const clusterRow = page.locator(`li:has-text("${clusterName}")`);
    await expect(clusterRow.getByText('PROVISIONING')).toBeVisible({ timeout: 10000 });
    await expect(clusterRow.getByText('RUNNING')).toBeVisible({ timeout: 180000 }); // Wait up to 3 minutes

    // 5. Open Command Runner and execute a command
    await clusterRow.getByRole('button', { name: 'Terminal' }).click();
    const terminal = page.locator('.fixed.inset-0'); // The terminal modal
    await expect(terminal).toBeVisible();
    await terminal.getByPlaceholder('e.g., kubectl get pods').fill('kubectl version');
    await terminal.getByRole('button', { name: 'Run' }).click();

    // Check for command output
    await expect(terminal.getByText(/Client Version/)).toBeVisible({ timeout: 30000 });
    await terminal.getByRole('button', { name: 'Close' }).click();
    await expect(terminal).not.toBeVisible();

    // 6. Delete the cluster
    await clusterRow.getByRole('button', { name: 'Delete' }).click();
    await expect(clusterRow.getByText('DELETING')).toBeVisible();

    // The SSE update should eventually remove the item from the DOM
    await expect(clusterRow).not.toBeVisible({ timeout: 30000 });
});
