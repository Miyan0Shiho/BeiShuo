package com.beishuo.common;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class Result<T> {
    private Boolean success;
    private String message;
    private T data;
    private ErrorInfo error;
    private String timestamp;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ErrorInfo {
        private String code;
        private String message;
        private Map<String, Object> details;
    }

    private static String getCurrentTimestamp() {
        return Instant.now().atZone(ZoneId.of("UTC"))
                .format(DateTimeFormatter.ISO_INSTANT);
    }

    public static <T> Result<T> success(T data) {
        Result<T> result = new Result<>();
        result.setSuccess(true);
        result.setMessage(ResultCode.SUCCESS.getMessage());
        result.setData(data);
        result.setTimestamp(getCurrentTimestamp());
        return result;
    }

    public static <T> Result<T> success(String message, T data) {
        Result<T> result = new Result<>();
        result.setSuccess(true);
        result.setMessage(message);
        result.setData(data);
        result.setTimestamp(getCurrentTimestamp());
        return result;
    }

    public static <T> Result<T> success() {
        return success(null);
    }

    public static <T> Result<T> error(ResultCode resultCode) {
        Result<T> result = new Result<>();
        result.setSuccess(false);
        result.setMessage(resultCode.getMessage());
        ErrorInfo errorInfo = new ErrorInfo();
        errorInfo.setCode(String.valueOf(resultCode.getCode()));
        errorInfo.setMessage(resultCode.getMessage());
        result.setError(errorInfo);
        result.setTimestamp(getCurrentTimestamp());
        return result;
    }

    public static <T> Result<T> error(ResultCode resultCode, String message) {
        Result<T> result = new Result<>();
        result.setSuccess(false);
        result.setMessage(message);
        ErrorInfo errorInfo = new ErrorInfo();
        errorInfo.setCode(String.valueOf(resultCode.getCode()));
        errorInfo.setMessage(message);
        result.setError(errorInfo);
        result.setTimestamp(getCurrentTimestamp());
        return result;
    }

    public static <T> Result<T> error(int code, String message) {
        Result<T> result = new Result<>();
        result.setSuccess(false);
        result.setMessage(message);
        ErrorInfo errorInfo = new ErrorInfo();
        errorInfo.setCode(String.valueOf(code));
        errorInfo.setMessage(message);
        result.setError(errorInfo);
        result.setTimestamp(getCurrentTimestamp());
        return result;
    }

    public static <T> Result<T> error(String code, String message, Map<String, Object> details) {
        Result<T> result = new Result<>();
        result.setSuccess(false);
        result.setMessage(message);
        ErrorInfo errorInfo = new ErrorInfo();
        errorInfo.setCode(code);
        errorInfo.setMessage(message);
        errorInfo.setDetails(details);
        result.setError(errorInfo);
        result.setTimestamp(getCurrentTimestamp());
        return result;
    }

    public static <T> Result<T> error(String message) {
        Result<T> result = new Result<>();
        result.setSuccess(false);
        result.setMessage(message);
        ErrorInfo errorInfo = new ErrorInfo();
        errorInfo.setCode(String.valueOf(ResultCode.INTERNAL_SERVER_ERROR.getCode()));
        errorInfo.setMessage(message);
        result.setError(errorInfo);
        result.setTimestamp(getCurrentTimestamp());
        return result;
    }
}

