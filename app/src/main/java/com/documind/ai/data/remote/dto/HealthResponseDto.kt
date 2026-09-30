package com.documind.ai.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * Data Transfer Object for backend health API response.
 */
data class HealthResponseDto(
    @SerializedName("status") val status: String,
    @SerializedName("service") val service: String? = null,
    @SerializedName("version") val version: String? = null,
    @SerializedName("environment") val environment: String? = null,
    @SerializedName("database") val database: String? = null
)
