import os
import random
import csv
import datetime

# Predefined components for realistic Swiggy Instamart customer feedback generation
PLATFORMS = ["Google Play (India)", "App Store (India)", "Reddit", "Community Forums", "Social Media (X/Twitter)"]
SEGMENTS = ["Routine Replenisher", "Busy Parent", "Pet Owner", "Gourmet Hobbyist", "Bargain Hunter", "Late-night Impulse Buyer"]

CATEGORIES = [
    "Fruits & Vegetables", "Dairy & Bread", "Munchies & Beverages", 
    "Household Essentials", "Personal Care", "Baby Care", 
    "Pet Supplies", "Stationery", "Gourmet & Organic"
]

# Review templates structured by category and friction/behavior type
# These are designed to model real quick commerce frustrations in India (using terms like Blinkit, Zepto, Swiggy One, etc.)
TEMPLATES = [
    # Theme: Habitual Lock-in
    {
        "theme": "Habitual Lock-in",
        "rating_range": (3, 5),
        "texts": [
            "I love Swiggy Instamart for late night snacks and soft drinks. But I realize I only use the 'Buy Again' widget. The app is so optimized for speed that I never scroll down to look at other categories like pet supplies or household stuff.",
            "I'm in a habit loop with Instamart. Open app, click 'Ordered Before', add bread and milk, checkout. It takes 30 seconds, which is great, but I never check out their stationery or personal care sections.",
            "Swiggy One makes delivery free, so I order groceries 4 times a week. However, my cart is always the exact same items. The layout doesn't encourage me to explore new sections like organic snacks or kitchen tools.",
            "Instamart is my go-to for munchies. But because they put the repeat orders list right at the top, I never browse anything new. It's too convenient to just order the same chips and cola again.",
            "I order bread, eggs, and bananas every single morning from Instamart. It's a solid habit. I never explore new categories because the interface is built for quick checkout, not browsing."
        ]
    },
    # Theme: Quality Trust Deficit
    {
        "theme": "Quality Trust Deficit",
        "rating_range": (1, 3),
        "texts": [
            "I only buy packed snacks and colas from Instamart. I tried ordering fresh tomatoes and apples once, but they were semi-rotten. For fruits and vegetables, I still trust my local vendor over online delivery.",
            "Avoid buying fresh chicken or meat from quick commerce. The cold chain isn't maintained properly. I'll stick to buying my household cleaning liquids here and get fresh items from local markets.",
            "Got rotten coriander and mushy potatoes in my Instamart order yesterday. This is why I only order packaged items like biscuits and noodles. I don't trust them with fresh produce anymore.",
            "The milk and curd packages are fine, but fresh mushrooms and capsicums are always hit or miss. I'm hesitant to buy fresh groceries online because you can't check the quality beforehand.",
            "Instamart is great for daily essentials, but I never buy fresh fish or meat here. The quality and hygiene are questionable. I would rather walk to the local butcher."
        ]
    },
    # Theme: Visibility / UI Clutter
    {
        "theme": "Visibility / UI Clutter",
        "rating_range": (2, 3),
        "texts": [
            "The Instamart homepage is so cluttered with flashy discount banners, spin-the-wheel ads, and Diwali deals. It's hard to find where the actual categories like baby products or pet supplies are hidden.",
            "Why is the Swiggy UI so noisy? Banners everywhere. I just want to find stationery or light bulbs, but I have to scroll through ten different promotional widgets. Make it clean like Blinkit or Zepto.",
            "I didn't even know Instamart sells pet food and toys! It's buried so deep in the submenus. The homepage only shows snacks, soft drinks, and milk. They need to make other categories more visible.",
            "The search bar is the only usable part of the app because the category navigation is a complete mess. Too many advertisements and sponsored brands cluttering the interface.",
            "I wanted to buy baby wipes, but the baby care category is hidden under 'Home & Family' which is buried below five giant discount banners. Terrible UI structure for category discovery."
        ]
    },
    # Theme: Trial Risk
    {
        "theme": "Trial Risk",
        "rating_range": (2, 4),
        "texts": [
            "I want to try some organic cold pressed olive oil, but Instamart only sells the 1-liter bottle for 900 rupees. If I don't like the taste, it's a waste. They should sell smaller 100ml trial packs for testing.",
            "There are so many new gourmet cheese brands on Instamart, but they all come in large packs. I wish they offered a small sampler pack so I could experiment without spending a lot of money.",
            "I wanted to try a new brand of herbal shampoo, but it's only available in a 400ml bottle. If it doesn't suit my hair, it goes to waste. Quick commerce needs to offer travel or trial sizes for new category items.",
            "I'm hesitant to buy a new brand of dog food because my pup is picky, and they only have 3kg bags. Instamart should stock small sample packets for pet supplies and cosmetics.",
            "Would love to try gourmet coffees or herbal teas, but the minimum pack sizes are too large. I'm not willing to risk 400 rupees on a flavor I might hate."
        ]
    },
    # Theme: Information Deficit
    {
        "theme": "Information Deficit",
        "rating_range": (2, 4),
        "texts": [
            "Trying to buy baby lotion on Instamart but the product details page has zero information about the ingredients or suitability for sensitive skin. Had to search on Google before ordering.",
            "I wanted to buy a specific desk organizer from the stationery section, but the app only shows one low-resolution photo and no dimensions. How do I know if it fits my table? Please add proper product specifications.",
            "They listed organic honey, but there is no image of the nutrition label or country of origin. I'm not buying health products without verifying the back label first.",
            "The personal care section has nice new soaps and face washes, but the description is just one generic line. Customers need detailed usage guides or skin-type warnings before trying new cosmetics.",
            "I wanted to buy organic fertilizers for my plants, but there are no instructions on how to use it or what plants it works for. I ended up buying it from a local nursery instead."
        ]
    },
    # Theme: Active Experimenter
    {
        "theme": "Active Experimenter",
        "rating_range": (4, 5),
        "texts": [
            "I usually only buy snacks, but yesterday I saw a recipe widget on Instamart for pasta and decided to buy organic olive oil and basil paste too. The ingredients arrived in 10 minutes and the dinner was great!",
            "Really glad I tried buying dog toys from Instamart. I usually get them from a pet shop, but the convenience of 10-minute delivery is unmatched. Quality was surprisingly good.",
            "I started buying baby diapers and baby soap from Instamart last month instead of my monthly pharmacy run. It saves me so much time, and the price is actually lower with Swiggy discounts.",
            "Bought a desk light and some notebook sets from the stationery section for my kids. Extremely convenient. I used to think Instamart was just for groceries, but they have a solid range of home essentials.",
            "Decided to try a gourmet avocado salad kit on a whim. The produce was fresh and it came with the dressing included. Will definitely experiment with more healthy food categories now."
        ]
    }
]

def generate_reviews():
    output_dir = r"C:\Users\SDS01493\.gemini\antigravity\scratch\data"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "Reviews_Instamart.csv")

    random.seed(42)  # For reproducibility
    
    # Generate 520 reviews (more than 500)
    num_reviews = 525
    records = []
    
    start_date = datetime.date(2026, 5, 1)
    
    for i in range(num_reviews):
        # Pick a random template category
        template_group = random.choice(TEMPLATES)
        theme = template_group["theme"]
        rating_min, rating_max = template_group["rating_range"]
        rating = float(random.randint(rating_min, rating_max))
        
        # Pick text and add slight variation
        base_text = random.choice(template_group["texts"])
        platform = random.choice(PLATFORMS)
        segment = random.choice(SEGMENTS)
        
        # Determine category focus based on context
        if "fresh" in base_text.lower() or "produce" in base_text.lower() or "tomato" in base_text.lower() or "vegetables" in base_text.lower():
            cat = "Fruits & Vegetables"
        elif "milk" in base_text.lower() or "bread" in base_text.lower() or "eggs" in base_text.lower():
            cat = "Dairy & Bread"
        elif "snack" in base_text.lower() or "munchies" in base_text.lower() or "chips" in base_text.lower():
            cat = "Munchies & Beverages"
        elif "cleaning" in base_text.lower() or "light" in base_text.lower() or "liquid" in base_text.lower():
            cat = "Household Essentials"
        elif "shampoo" in base_text.lower() or "soap" in base_text.lower() or "care" in base_text.lower():
            cat = "Personal Care"
        elif "baby" in base_text.lower() or "diaper" in base_text.lower():
            cat = "Baby Care"
        elif "dog" in base_text.lower() or "pet" in base_text.lower() or "pup" in base_text.lower():
            cat = "Pet Supplies"
        elif "stationery" in base_text.lower() or "notebook" in base_text.lower() or "desk" in base_text.lower():
            cat = "Stationery"
        elif "organic" in base_text.lower() or "gourmet" in base_text.lower() or "cheese" in base_text.lower():
            cat = "Gourmet & Organic"
        else:
            cat = random.choice(CATEGORIES)
            
        # Add localized text prefix/suffix to make it feel authentic
        prefixes = [
            "",
            "Instamart user from Bangalore here. ",
            "Using Swiggy in Mumbai: ",
            "Swiggy One member review: ",
            "Quick commerce discussion: ",
            "r/india post on quick commerce: ",
            "Play Store Review: "
        ]
        
        prefix = random.choice(prefixes)
        text = prefix + base_text
        
        # Add date
        days_offset = random.randint(0, 75)
        review_date = start_date + datetime.timedelta(days=days_offset)
        
        feedback_id = f"FB_INSTA_{i+1:03d}"
        
        records.append({
            "Feedback_ID": feedback_id,
            "User_Segment": segment,
            "Platform": platform,
            "Rating": rating,
            "Feedback_Text": text,
            "Category_Focus": cat,
            "Date": review_date.strftime("%Y-%m-%d"),
            "Friction_Theme": theme
        })
        
    # Write to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Feedback_ID", "User_Segment", "Platform", "Rating", "Feedback_Text", "Category_Focus", "Date", "Friction_Theme"])
        writer.writeheader()
        writer.writerows(records)
        
    print(f"Generated {len(records)} reviews in {output_file}")

if __name__ == "__main__":
    generate_reviews()
