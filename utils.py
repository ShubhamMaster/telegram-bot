def fetch_erp_data(prn):
    import requests
    from bs4 import BeautifulSoup
    import base64
    import json

    try:
        if not prn.isdigit() or len(prn) != 12:
            return {"error": "❌ Invalid PRN. Please enter a 12-digit number."}

        encoded_prn = base64.b64encode(prn.encode()).decode()
        url = f"https://erp.sandipuniversity.com/examination/view_form/{encoded_prn}"

        with open("session.json", "r") as f:
            cookies = json.load(f)

        response = requests.get(url, cookies=cookies, timeout=10)
        if response.status_code != 200 or "login" in response.url:
            return {"error": "🔒 Session expired or login page shown. Update session.json."}

        soup = BeautifulSoup(response.text, "html.parser")
        heading = soup.find("h2")
        page_title = heading.text.strip() if heading else "ERP Page Loaded"

        result = {"PageTitle": page_title}
        table = soup.find("table", class_="table-bordered")

        if not table:
            return {"error": "⚠️ Table not found on page."}

        rows = table.find_all("tr")
        if len(rows) <= 1:
            return {"error": "⚠️ No data found in ERP table."}

        for row in rows[1:]:
            cells = row.find_all(["th", "td"])
            for i in range(0, len(cells), 2):
                if i + 1 < len(cells):
                    key = cells[i].text.strip().replace(":", "")
                    value = cells[i + 1].text.strip()
                    if key and value:
                        result[key] = value

        return result if len(result) > 1 else {"error": "⚠️ Data structure invalid."}

    except Exception as e:
        return {"error": f"🔥 Unexpected error: {str(e)}"}
