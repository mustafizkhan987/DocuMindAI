package com.documind.ai.data.repository

import com.documind.ai.core.common.Result
import com.documind.ai.data.remote.api.DocuMindApi
import com.documind.ai.domain.model.BackendHealth
import com.documind.ai.domain.model.Document
import com.documind.ai.domain.repository.DocumentRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

/**
 * Concrete repository implementation of DocumentRepository.
 *
 * Task 3: Provides local/mock state architecture.
 * Task 4: Will wire live Retrofit API calls using docuMindApi.
 */
class DocumentRepositoryImpl(
    private val api: DocuMindApi
) : DocumentRepository {

    override suspend fun getBackendHealth(): Result<BackendHealth> {
        return try {
            val response = api.getV1Health()
            if (response.isSuccessful) {
                val body = response.body()
                if (body != null) {
                    Result.Success(
                        BackendHealth(
                            isConnected = body.status == "ok",
                            status = if (body.status == "ok") "Connected" else "Status: ${body.status}",
                            serviceName = body.service ?: "DocuMind AI API",
                            version = body.version ?: "0.1.0",
                            databaseStatus = body.database ?: "unknown"
                        )
                    )
                } else {
                    Result.Error(Exception("Empty response body"), "Server returned empty response")
                }
            } else {
                Result.Error(Exception("HTTP error: ${response.code()}"), "Failed to connect to backend: HTTP ${response.code()}")
            }
        } catch (e: Exception) {
            Result.Error(e, "Connection failed: ${e.localizedMessage}")
        }
    }

    override fun getRecentDocuments(): Flow<List<Document>> = flow {
        // Task 4: Empty list placeholder for recent documents for now
        emit(emptyList())
    }
}
