"""Checklist CRUD. Driven from a phone/browser since the TV is read-only."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_session
from ..models import ChecklistItem, utcnow
from ..scheduler import broadcast_snapshot
from ..schemas import ChecklistItemIn, ChecklistItemOut, ChecklistItemPatch

router = APIRouter(prefix="/api/checklist", tags=["checklist"])


def _out(item: ChecklistItem) -> ChecklistItemOut:
    return ChecklistItemOut(
        id=item.id, text=item.text, done=item.done, position=item.position, assignee=item.assignee
    )


@router.get("", response_model=list[ChecklistItemOut])
def list_items(db: Session = Depends(get_session)):
    rows = db.scalars(
        select(ChecklistItem).order_by(ChecklistItem.position, ChecklistItem.id)
    ).all()
    return [_out(r) for r in rows]


@router.post("", response_model=ChecklistItemOut, status_code=201)
async def create_item(body: ChecklistItemIn, db: Session = Depends(get_session)):
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="text is required")
    next_pos = (db.scalar(select(func.max(ChecklistItem.position))) or 0) + 1
    item = ChecklistItem(text=text, assignee=body.assignee, position=next_pos)
    db.add(item)
    db.commit()
    await broadcast_snapshot()
    return _out(item)


@router.patch("/{item_id}", response_model=ChecklistItemOut)
async def update_item(item_id: int, body: ChecklistItemPatch, db: Session = Depends(get_session)):
    item = db.get(ChecklistItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    if body.text is not None:
        item.text = body.text.strip()
    if body.assignee is not None:
        item.assignee = body.assignee
    if body.position is not None:
        item.position = body.position
    if body.done is not None:
        item.done = body.done
        item.done_at = utcnow() if body.done else None
    db.commit()
    await broadcast_snapshot()
    return _out(item)


@router.post("/{item_id}/toggle", response_model=ChecklistItemOut)
async def toggle_item(item_id: int, db: Session = Depends(get_session)):
    item = db.get(ChecklistItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    item.done = not item.done
    item.done_at = utcnow() if item.done else None
    db.commit()
    await broadcast_snapshot()
    return _out(item)


@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int, db: Session = Depends(get_session)):
    item = db.get(ChecklistItem, item_id)
    if item:
        db.delete(item)
        db.commit()
        await broadcast_snapshot()
