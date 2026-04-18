def scoring_agent(company, industry, insights):
    # simple logic (lightweight)
    if "AI" in insights:
        return 90
    return 75