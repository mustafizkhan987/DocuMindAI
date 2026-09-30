package com.documind.ai.domain.model

/**
 * Domain representation of backend health status.
 */
data class BackendHealth(
    val isConnected: Boolean,
    val status: String,
    val serviceName: String = "DocuMind AI",
    val version: String = "0.1.0",
    val databaseStatus: String = "unknown"
)
