from pydantic import BaseModel
from typing import List, Dict, Optional

class Policy(BaseModel):
    privacy_policy: Optional[str]
    return_policy: Optional[str]
    terms_and_conditions: Optional[str]

class ContactDetails(BaseModel):
    emails: List[str]
    phone_numbers: List[str]

class SocialHandles(BaseModel):
    instagram: Optional[str]
    facebook: Optional[str]
    tiktok: Optional[str]
    twitter: Optional[str]

class FAQ(BaseModel):
    question: str
    answer: str

class BrandInsights(BaseModel):
    brand_name: str
    products: List[Dict]
    hero_products: List[Dict]
    policies: Policy
    faqs: List[FAQ]
    social_handles: SocialHandles
    contact_details: ContactDetails
    about: Optional[str]
    important_links: List[str]
