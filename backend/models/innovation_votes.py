"""
Innovation voting system models
Allows users to vote on whether innovations meet inclusion criteria
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from models.database import Base
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class InnovationVote(Base):
    """Votes on whether innovations meet inclusion criteria for AI innovations in Africa"""

    __tablename__ = "innovation_votes"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    innovation_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), ForeignKey("innovations.id"), nullable=False
    )
    voter_identifier: Mapped[str] = mapped_column(
        String, nullable=False
    )  # Hashed email/IP for deduplication
    vote_type: Mapped[str] = mapped_column(
        String, nullable=False
    )  # 'yes', 'no', 'need_more_info'
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Metadata for ML training
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ip_hash: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )  # For fraud prevention

    # Relationships
    innovation = relationship("Innovation")
