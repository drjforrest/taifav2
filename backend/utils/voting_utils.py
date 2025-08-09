"""
Utility functions for innovation voting system
"""

from uuid import UUID
from loguru import logger


async def update_innovation_verification_status(innovation_id: UUID):
    """Update innovation verification status based on votes"""
    try:
        from config.database import get_supabase

        supabase = get_supabase()

        # Get all votes for this innovation
        votes_response = supabase.table("innovation_votes").select("vote_type").eq("innovation_id", str(innovation_id)).execute()
        votes = votes_response.data if votes_response.data else []

        if not votes:
            return

        # Count votes by type
        yes_votes = len([v for v in votes if v["vote_type"] == "yes"])
        no_votes = len([v for v in votes if v["vote_type"] == "no"])
        need_more_info_votes = len([v for v in votes if v["vote_type"] == "need_more_info"])
        total_votes = len(votes)

        # Compute new verification status
        new_status = compute_verification_status(yes_votes, no_votes, need_more_info_votes, total_votes)

        # Update the innovation
        supabase.table("innovations").update({"verification_status": new_status}).eq("id", str(innovation_id)).execute()

        logger.info(f"Updated verification status for innovation {innovation_id} to {new_status}")

    except Exception as e:
        logger.error(f"Error updating verification status for innovation {innovation_id}: {e}")


def compute_verification_status(yes_votes: int, no_votes: int, need_more_info_votes: int, total_votes: int) -> str:
    """Compute verification status based on vote counts"""
    if total_votes == 0:
        return "pending"
    
    # If we have at least 3 votes, use majority rule
    if total_votes >= 3:
        yes_ratio = yes_votes / total_votes
        no_ratio = no_votes / total_votes
        
        # Strong consensus (>70%) gets verified/rejected status
        if yes_ratio >= 0.7:
            return "community"  # Community validated
        elif no_ratio >= 0.7:
            return "pending"    # Keep as pending, don't reject outright
        else:
            return "pending"    # No clear consensus
    
    # With fewer than 3 votes, need unanimous or strong majority
    if total_votes == 1:
        return "pending"  # Single votes don't change status
    elif total_votes == 2:
        if yes_votes == 2:
            return "community"
        else:
            return "pending"
    
    return "pending"