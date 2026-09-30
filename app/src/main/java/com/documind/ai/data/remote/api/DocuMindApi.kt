package com.documind.ai.data.remote.api

import com.documind.ai.data.remote.dto.HealthResponseDto
import retrofit2.Response
import retrofit2.http.GET

/**
 * Retrofit REST API interface for DocuMind AI FastAPI backend.
 *
 * Task 3: Prepared interface for Task 4 backend connection.
 */
interface DocuMindApi {

    @GET("api/v1/health")
    suspend fun getV1Health(): Response<HealthResponseDto>

    @GET("health")
    suspend fun getHealth(): Response<HealthResponseDto>
}
