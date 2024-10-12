from datetime import datetime, timedelta

def get_yesterday():
    """
        Returns the date of yesterday.
        
        Returns:
            datetime.date: The date of yesterday.
    """
    return (datetime.today()-timedelta(days=1)).date() 