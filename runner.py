from collections import namedtuple
from datetime import datetime, timedelta
import os.path
import pdb
import re
from typing import List

# Project imports
import insta
from insta import ParsedPost
import sheet

# Posts older than this number of days will get cleared out
MAX_AGE_DAYS = 30

def merge_and_filter_posts(posts1, posts2):
    """
    Merge 2 posts list by id and return them in descending time.
    Also filter out posts that are older than a month
    """
    posts1_by_reel_url = {post.reel_url : post for post in posts1}
    posts2_by_reel_url = {post.reel_url : post for post in posts2}
    for post_url, post in posts2_by_reel_url.items():
        if post_url not in posts1_by_reel_url:
            posts1_by_reel_url[post_url] = post
    merged_posts = sorted(list(posts1_by_reel_url.values()), key=lambda post: post.time, reverse=True)
    
    cutoff_date = datetime.now() - timedelta(days=MAX_AGE_DAYS)

    recent_posts = [post for post in merged_posts if datetime.strptime(post.date, "%Y/%m/%d") >= cutoff_date]
    return recent_posts

def print_user_stats(posts):
    tally = {}
    for post in posts:
        account_name = post.account_name
        tally[account_name] = tally.get(account_name, 0) + 1

    # Sort the tally in descending order of occurrence
    sorted_tally = sorted(tally.items(), key=lambda x: x[1], reverse=True)

    # Print the tally in descending order
    for account_name, count in sorted_tally:
        print(f"{account_name}: {count}")

if __name__ == "__main__":
    """
    # Re-enable this to debug.
    insta.debug_one_account("kmckayclimbs098")
    if True:
        exit()
    """
    print("Scraping instagram...")
    posts_from_insta = insta.get_all_recent_posts()
    
    print("Reading from spreadsheet...")
    sheet_client = sheet.get_sheet_client()
    posts_from_sheet = sheet.read_from_spreadsheet(sheet_client)
    
    posts_final = merge_and_filter_posts(posts_from_insta, posts_from_sheet)

    print("Writing to spreadsheet...")
    sheet.write_to_spreadsheet(sheet_client, posts_final)

    print("User stats:")
    print_user_stats(posts_final)
