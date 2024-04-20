# Get all insta recent posts
# See get_all_recent_posts()
from collections import namedtuple
import instaloader
import os.path
import pdb
import re
from typing import List
from tqdm import tqdm

ParsedPost = namedtuple('ParsedPost', ['account_name', 'grade', 'date', 'time', 'caption', 'reel_url', 'photo_url', 'gym_location'])

"""
Accounts to scrape from
E.g. https://www.instagram.com/monke._.mode/
"""
WHITELISTED_INSTA_ACCOUNTS = [
    "monke._.mode",
    "ccf.climbs",
    "climb.try.again",
    "littlebox.climbs",
    "danlebuiclimb",
    "ccf.climbs",
    "tiffnyclimbs",
    "m.j.climbing",
    "tiff.plus.ed.climb",
    "climb.on.kev.on",
    "jason_boulders",
    "wl.climbs",
]

"""
How many recent posts to filter for
"""
# 30 because 1 post per day, and we're only keeping entries in the past month
NUM_RECENT_POSTS = 30

# Create an instance of Instaloader
L = instaloader.Instaloader()
L.login("monke._.mode", open('secret/insta_password.txt', 'r').read())


def get_all_recent_posts():
    parsed_posts = []
    for account_name in tqdm(WHITELISTED_INSTA_ACCOUNTS):
        print(f"Processing posts from {account_name}")
        parsed_posts.extend(query_recent_posts(account_name, NUM_RECENT_POSTS))
    return parsed_posts

def query_recent_posts(account_name: str, num_recent_posts: int) -> List[ParsedPost]:
    """
    Get recent climbing-related reels from `account_name`
    """
    try:
        # Retrieve profile metadata
        profile = instaloader.Profile.from_username(L.context, account_name)
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Profile '{account_name}' does not exist.")

    num_post = 0 
    parsed_posts = []
    # Iterate over recent posts
    for post in profile.get_posts():
        num_post += 1

        if num_post > NUM_RECENT_POSTS:
            break
        if not is_climbing_post(post):
            continue

        post_tokens = set(post.caption.lower().split())
        # Extract post fields
        grade = get_post_grade(post, post_tokens)
        if grade == None:
            continue
        reel_url = f"https://www.instagram.com/reel/{post.shortcode}"
        photo_url = post.url
        date_str = post.date.strftime("%Y/%m/%d")
        full_date_str = post.date.strftime("%Y-%m-%d %H:%M:%S")
        gym_location = get_gym_location(account_name, post_tokens, post)
        if gym_location is None:
            gym_location = ""
        parsed_posts.append(
            ParsedPost(account_name,
                grade,
                date_str,
                full_date_str,
                post.caption,
                reel_url,
                photo_url,
                gym_location))
    return parsed_posts


def is_climbing_post(post):
    if post.typename != "GraphVideo":
        return False
    if not post.caption:
        return False
    if "seattleboulderingproject" in post.tagged_users:
        return True
    if "seattleboulderingproject" in post.caption_hashtags:
        return True
    return False


grade_map = {
    "yellow": "VB",
    "red": "V0-2",
    "green": "V1-3",
    "purple": "V2-4",
    "🟣": "V2-4",
    "orange": "V3-5",
    "🧡": "V3-5",
    "black": "V4-6",
    "🖤": "V4-6",
    "⚫️": "V4-6",
    "blue": "V5-7",
    "🔵": "V5-7",
    "pink": "V6-8",
    "🩷": "V6-8",
    "🌸":"V6-8",
    "white": "V7+",
    "🤍": "V7+"
}
def get_post_grade(post, post_tokens):
    """
    return val:str. E.g. "V3-5"
    Or None if not found.

    2 passes:
    1. Grade range. E.g."V3-5"
    2. Color. E.g. "orange"
    """
    caption = post.caption

    # First pass: Check for grade range string like "V3-5"
    match = re.search(r'V\d+-\d+', caption)
    if match:
        return match.group()

    # Second pass: Check for color
    for color, grade in grade_map.items():
        if color in post_tokens:
            return grade
    return None


gym_locations = {"poplar", "fremont"}
def get_gym_location(account_name, post_tokens, post):
    locs = gym_locations.intersection(post_tokens)
    if len(locs) > 0:
        return locs.pop()

    if account_name == "monke._.mode":
        return "poplar"


    if "seattleboulderingprojectfremont" in post.caption_hashtags:
        return "fremont"
    elif "seattleboulderingprojectpoplar" in post.caption_hashtags:
        return "poplar"
    return None