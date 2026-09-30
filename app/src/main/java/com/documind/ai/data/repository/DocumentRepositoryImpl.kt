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
        // Task 3: Return local state (Not Connected until Task 4 live API integration)
        return Result.Success(
            BackendHealth(
                isConnected = false,
                status = "Not Connected",
                serviceName = "DocuMind AI API",
                version = "0.1.0",
                databaseStatus = "Not Connected"
            )
        )
    }

    override fun getRecentDocuments(): Flow<List<Document>> = flow {
        // Task 3: Empty list placeholder for recent documents
        emit(emptyList())
    }
}
