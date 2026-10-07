// =========================================================
// ATHENA LIVE BACKEND DATA
// =========================================================

export const campaigns = [];
export const products = [];
export const findings = [];
export const trend = [];

export const summary = {
    ad_spend: 0,
    revenue: 0,
    roas: 0,
    contribution: 0,
    campaign_count: 0,
};

export async function loadDashboard() {

    const response = await fetch(
        "http://127.0.0.1:8000/api/dashboard"
    );

    if (!response.ok) {
        throw new Error(
            `Athena API returned ${response.status}`
        );
    }

    const data = await response.json();

    // Update existing arrays instead of replacing them.
    campaigns.splice(
        0,
        campaigns.length,
        ...(data.campaigns || [])
    );

    products.splice(
        0,
        products.length,
        ...(data.products || [])
    );

    findings.splice(
        0,
        findings.length,
        ...(data.findings || [])
    );

    trend.splice(
        0,
        trend.length,
        ...(data.trend || [])
    );

    // Update the existing summary object.
    summary.ad_spend =
        data.summary?.ad_spend || 0;

    summary.revenue =
        data.summary?.revenue || 0;

    summary.roas =
        data.summary?.roas || 0;

    summary.contribution =
        data.summary?.contribution || 0;

    summary.campaign_count =
        data.summary?.campaign_count || 0;

    return data;
}