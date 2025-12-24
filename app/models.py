import datetime
import enum
import uuid
from sqlalchemy import (
    Column, Float, Integer, String, ForeignKey, DateTime, JSON, UniqueConstraint, Enum
)
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func


EmployeeRole = {"ADMIN", "EQUIPMENT_MANAGER", "FACTORY_MANAGER", "STAFF"}

skill_list = [
    {"key": "operation_machine", "label": "Vận hành máy móc"},
    {"key": "maintenance", "label": "Bảo trì máy móc"},
    {"key": "quality_control", "label": "Kiểm soát chất lượng"},
    {"key": "safety_compliance", "label": "Tuân thủ an toàn"},
    {"key": "assembly", "label": "Lắp ráp sản phẩm"},
]


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    phoneNumber = Column(String)
    name = Column(String, nullable=False)


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    email = Column(String)
    phoneNumber = Column(String)
    fax = Column(String)
    owner = Column(Integer, ForeignKey("admin.id", ondelete="CASCADE"))
    domain = Column(String)
    # relationship to owner
    admin = relationship("Admin", backref="companies")

    # relationship to equipment manager
    equipementManagerId = Column(
        Integer, ForeignKey("employee.id"), unique=True)
    equipementManager = relationship(
        "Employee",
        foreign_keys=[equipementManagerId],
        backref="managed_company"
    )

    employee_factory_distances = relationship(
        "EmployeeToFactoryDistance",
        back_populates="company",
        cascade="all, delete-orphan"
    )


# class LocationType(enum.Enum):
#     factory = "factory"
#     residence = "residence"
#     private_house = "private_house"


# class Location(Base):
#     __tablename__ = "location"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     address = Column(String, nullable=True)
#     type = Column(Enum(LocationType), nullable=False)
#     companyId = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))
#     company = relationship("Company", backref="locations")


# class LocationDistances(Base):
#     __tablename__ = "location_distances"

#     measure_point = Column(Integer, ForeignKey(
#         "location.id"), primary_key=True)
#     reference_point = Column(Integer, ForeignKey(
#         "location.id"), primary_key=True)
#     travel_hours = Column(Integer)


class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer, primary_key=True, index=True)
    companyId = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))
    email = Column(String, nullable=False, unique=True, index=True)
    fullName = Column(String, nullable=False)
    password = Column(String, nullable=False)
    phoneNumber = Column(String)
    employeeSkillList = Column(JSON)
    roleList = Column(JSON)
    company = relationship("Company", foreign_keys=[
                           companyId], backref="employees")


class CycleStatus(enum.Enum):
    draft = "draft"
    processing = "processing"
    pause = "pause"
    finish = "finish"
    drop = "drop"


class FactoryCycle(Base):
    __tablename__ = "factory_cycle"

    id = Column(Integer, primary_key=True, index=True)
    factoryId = Column(Integer, ForeignKey("factory.id", ondelete="CASCADE"))

    name = Column(String, nullable=False)
    description = Column(String)
    # cycle_schedula = Column(JSON)
    # lịch trình
    startTime = Column(DateTime, nullable=True)
    endTime = Column(DateTime, nullable=True)

    # trạng thái chu kỳ
    # draft / scheduling / running / completed

    status = Column(
        Enum(
            CycleStatus,
        ),
        nullable=False,
        default=CycleStatus.draft,
    )

    factory = relationship("Factory", backref="cycles")

    # 👇 QUAN TRỌNG
    jobs = relationship(
        "JobByMachine",
        back_populates="cycle",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class CycleDetail(Base):
    __tablename__ = "cycle_detail"
    id = Column(Integer, primary_key=True, index=True)
    factoryCycleId = Column(Integer, ForeignKey(
        "factory_cycle.id", ondelete="CASCADE"))

    machineId = Column(Integer, ForeignKey(
        "machine.id", ondelete="CASCADE"))


class FactoryDistance(Base):
    __tablename__ = "factory_distance"

    id = Column(Integer, primary_key=True, index=True)

    companyId = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))

    # Nhà máy xuất phát
    factory_from_id = Column(
        Integer,
        ForeignKey("factory.id", ondelete="CASCADE"),
        nullable=False
    )
    company = relationship(
        "Company", backref="factoriyDistances", lazy="noload")

    # Nhà máy đích
    factory_to_id = Column(
        Integer,
        ForeignKey("factory.id", ondelete="CASCADE"),
        nullable=False
    )

    # Khoảng cách (km)
    distance_km = Column(Integer)

    # Thời gian di chuyển (giờ)
    travel_time_hours = Column(Integer)

    # Relationship (optional)
    factory_from = relationship("Factory", foreign_keys=[
                                factory_from_id], lazy="joined")
    factory_to = relationship("Factory", foreign_keys=[
                              factory_to_id], lazy="joined")

    # Unique constraint để không tạo cặp trùng nhau
    __table_args__ = (
        UniqueConstraint("factory_from_id", "factory_to_id",
                         name="uq_factory_distance_pair"),
    )


class EmployeeToFactoryDistance(Base):
    __tablename__ = "employee_to_factory_distance"

    id = Column(Integer, primary_key=True, index=True)

    companyId = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))

    # Nhà máy xuất phát
    factoryId = Column(
        Integer,
        ForeignKey("factory.id", ondelete="CASCADE"),
        nullable=False
    )

    company = relationship(
        "Company",
        back_populates="employee_factory_distances",
        lazy="noload"
    )
    # Nhà máy đích
    employeeId = Column(
        Integer,
        ForeignKey("employee.id", ondelete="CASCADE"),
        nullable=False
    )

    # Khoảng cách (km)
    distance_km = Column(Integer)

    # Thời gian di chuyển (giờ)
    travel_time_hours = Column(Integer)

    # Unique constraint để không tạo cặp trùng nhau
    __table_args__ = (
        UniqueConstraint("employeeId", "factoryId",
                         name="uq_factory_and_em_distance_pair"),
    )


class Factory(Base):
    __tablename__ = "factory"
    id = Column(Integer, primary_key=True, index=True)
    companyId = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    description = Column(String)
    factoryManager = Column(Integer, ForeignKey("employee.id"), unique=True)
    company = relationship("Company", backref="factories", lazy="noload")
    manager = relationship("Employee", lazy="noload")


class RequestStatus(str, enum.Enum):
    pending = "pending"     # mới tạo, chờ phê duyệt
    approved = "approved"   # được đồng thuận
    rejected = "rejected"   # bị từ chối
    cancelled = "cancelled"  # người tạo hủy


class MachineInFactory(Base):
    __tablename__ = "machine_in_factory"

    id = Column(Integer, primary_key=True, index=True)

    factoryId = Column(Integer, ForeignKey(
        "factory.id", ondelete="CASCADE"), nullable=False)
    machineId = Column(Integer, ForeignKey(
        "machine.id", ondelete="CASCADE"), nullable=False)
    companyId = Column(Integer, ForeignKey(
        "company.id", ondelete="CASCADE"), nullable=False)

    status = Column(Enum(RequestStatus),
                    default=RequestStatus.pending, nullable=False)
    managerComment = Column(String(500))  # comment khi approve/reject

    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())

    # unique constraint
    __table_args__ = (
        UniqueConstraint("factoryId", "machineId", name="uq_factory_machine"),
    )
    # relationships
    factory = relationship("Factory", backref="machines_in_factory")
    machine = relationship("Machine", backref="machine_in_factories")
    company = relationship("Company", backref="machines_in_factory")


class Machine(Base):
    __tablename__ = "machine"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    type = Column(String(50))
    code = Column(String, unique=True)
    companyId = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))
    manual_url = Column(String(255))
    vendor = Column(String(100))
    note = Column(String(500))
    company = relationship("Company", backref="machines")

    job_ops = relationship("JobByMachineOperate", back_populates="machine")


class JobByMachine(Base):
    __tablename__ = "job_by_machine"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)

    factoryCycleId = Column(
        Integer,
        ForeignKey("factory_cycle.id", ondelete="CASCADE")
    )

    cycle = relationship(
        "FactoryCycle",
        back_populates="jobs"
    )

    job_ops = relationship(
        "JobByMachineOperate",
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
                order_by="JobByMachineOperate.task_index"
    )


class JobByMachineOperate(Base):
    __tablename__ = "job_by_machine_operate"

    id = Column(Integer, primary_key=True, index=True)
    duration = Column(Float)

    machineId = Column(
        Integer,
        ForeignKey("machine.id", ondelete="CASCADE")
    )

    jobId = Column(
        Integer,
        ForeignKey("job_by_machine.id", ondelete="CASCADE")
    )

    start = Column(Float)
    end = Column(Float)
    task_index = Column(Integer)

    machine = relationship("Machine", back_populates="job_ops")
    job = relationship("JobByMachine", back_populates="job_ops")

    @property
    def machineCode(self) -> str | None:
        return self.machine.code if self.machine else None


class JobStatus(enum.Enum):
    planning = "planning"
    pending = "pending"
    finish = "finish"


class JobByEmployee(Base):
    __tablename__ = "job_by_employee"

    id = Column(Integer, primary_key=True, index=True)

    companyId = Column(
        Integer,
        ForeignKey("company.id", ondelete="CASCADE"),
        nullable=False
    )

    employeeId = Column(
        Integer,
        ForeignKey("employee.id", ondelete="SET NULL"),
        nullable=True
    )

    factoryId = Column(
        Integer,
        ForeignKey("factory.id", ondelete="SET NULL"),
        nullable=True
    )

    # ===== Thông tin job =====
    duration = Column(Integer)  # tổng số giờ
    name = Column(String)
    skillNeeded = Column(String)
    description = Column(String)

    # ===== Kế hoạch theo tuần =====
    expected_weekday = Column(Integer)
    # 0=Monday ... 6=Sunday

    start_hour = Column(Integer)
    # ví dụ: 8 = 8h sáng

    end_hour = Column(Integer)
    # ví dụ: 17 = 5h chiều

    # ===== Trạng thái =====
    status = Column(
        Enum(JobStatus),
        nullable=False,
        default=JobStatus.planning
    )

    # ===== Thời gian thực tế =====
    finishDate = Column(DateTime, nullable=True)

    # Relationships
    company = relationship("Company")
    employee = relationship("Employee", backref="jobs")
    factory = relationship("Factory")


class EmployeeBlockTime(Base):
    __tablename__ = "employee_block_time"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String)
    job_duration = Column(Integer)
    employee_id = Column(Integer, ForeignKey(
        "employee.id", ondelete="CASCADE"))
    requested_datetime = Column(DateTime)

    title = Column(String)
    description = Column(String)
    employee = relationship("Employee", backref="blocked_times")
