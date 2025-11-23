package com.beishuo.common.exception;

import com.beishuo.common.ResultCode;

public class UnauthorizedException extends BusinessException {
    public UnauthorizedException() {
        super(ResultCode.UNAUTHORIZED);
    }

    public UnauthorizedException(String message) {
        super(ResultCode.UNAUTHORIZED, message);
    }
}

