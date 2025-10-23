from fastapi import HTTPException, status


invalid_token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token",
    headers={"Authorization": "Bearer"},
)
