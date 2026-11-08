from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentOut, DepartmentUpdate

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=list[DepartmentOut])
async def list_departments(
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin", "manager")),
):
    result = await db.execute(select(Department).where(Department.is_active.is_(True)))
    items = result.scalars().all()
    return [DepartmentOut.model_validate(item) for item in items]


@router.post("", response_model=DepartmentOut)
async def create_department(
    payload: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    if payload.code:
        existing = await db.scalar(
            select(Department).where((Department.name == payload.name) | (Department.code == payload.code))
        )
        if existing is not None:
            raise ConflictException(message="Department with this name or code already exists")
    else:
        existing = await db.scalar(select(Department).where(Department.name == payload.name))
        if existing is not None:
            raise ConflictException(message="Department with this name already exists")

    department = Department(**payload.model_dump())
    db.add(department)
    await db.commit()
    await db.refresh(department)
    return DepartmentOut.model_validate(department)


@router.get("/{department_id}", response_model=DepartmentOut)
async def get_department(
    department_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_user),
):
    department = await db.get(Department, department_id)
    if department is None:
        raise NotFoundException(message="Department not found")
    return DepartmentOut.model_validate(department)


@router.put("/{department_id}", response_model=DepartmentOut)
async def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    department = await db.get(Department, department_id)
    if department is None:
        raise NotFoundException(message="Department not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(department, field, value)
    await db.commit()
    await db.refresh(department)
    return DepartmentOut.model_validate(department)


@router.delete("/{department_id}")
async def delete_department(
    department_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    department = await db.get(Department, department_id)
    if department is None:
        raise NotFoundException(message="Department not found")
    department.is_active = False
    await db.commit()
    return {"message": "Department deactivated successfully"}
