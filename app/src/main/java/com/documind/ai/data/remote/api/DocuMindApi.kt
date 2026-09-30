package com.documind.ai.data.remote.api

import com.documind.ai.data.remote.dto.DocumentUploadResponseDto
import com.documind.ai.data.remote.dto.HealthResponseDto
import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

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

    @Multipart
    @POST("api/v1/documents/upload")
    suspend fun uploadDocument(@Part file: MultipartBody.Part): Response<DocumentUploadResponseDto>
}
