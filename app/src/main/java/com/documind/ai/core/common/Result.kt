package com.documind.ai.core.common

/**
 * Generic result wrapper sealed class for handling data operations and UI states.
 */
sealed class Result<out T> {
    data class Success<out T>(val data: T) : Result<T>()
    data class Error(val exception: Throwable, val message: String? = exception.localizedMessage) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
