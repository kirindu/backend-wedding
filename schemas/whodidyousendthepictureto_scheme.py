def who_did_you_send_the_picture_to_helper(whoDidYouSendThePictureTo) -> dict:
    return {
        "id": str(whoDidYouSendThePictureTo["_id"]),

        "whoDidYouSendThePictureToName": whoDidYouSendThePictureTo.get("whoDidYouSendThePictureToName"),

        # SOFT DELETE FIELD
        "active": whoDidYouSendThePictureTo.get("active", True),

        # AUDIT FIELDS
        "createdBy": str(whoDidYouSendThePictureTo["createdBy"]) if whoDidYouSendThePictureTo.get("createdBy") else None,
        "updatedBy": str(whoDidYouSendThePictureTo["updatedBy"]) if whoDidYouSendThePictureTo.get("updatedBy") else None,
        "createdAt": whoDidYouSendThePictureTo["createdAt"].isoformat() if whoDidYouSendThePictureTo.get("createdAt") else None,
        "updatedAt": whoDidYouSendThePictureTo["updatedAt"].isoformat() if whoDidYouSendThePictureTo.get("updatedAt") else None,
    }