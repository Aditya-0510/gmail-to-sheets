from googleapiclient.discovery import build

def get_sheets_service(creds): #create google sheet api instance
    return build('sheets', 'v4', credentials=creds)

def append_to_sheet(service, spreadsheet_id, range_name, values): #to append data to the sheets
    if not values:
        print("No data to append.")
        return

    body = {
        'values': values
    }

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    print(f"{result.get('updates').get('updatedCells')} cells updated.")
