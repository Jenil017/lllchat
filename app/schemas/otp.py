"""Pydantic schemas for OTP verification."""

from pydantic import BaseModel, EmailStr, Field


class SendOTPRequest(BaseModel):
    """Request schema for sending OTP."""

    email: EmailStr = Field(..., description="Email address to send OTP")


class SendOTPResponse(BaseModel):
    """Response schema for sending OTP."""

    message: str
    email: str


class VerifyOTPRequest(BaseModel):
    """Request schema for verifying OTP."""

    email: EmailStr = Field(..., description="Email address")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class VerifyOTPResponse(BaseModel):
    """Response schema for OTP verification."""

    message: str
    verified: bool
