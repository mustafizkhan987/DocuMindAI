package com.documind.ai.ui.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.documind.ai.ui.components.DocuMindPrimaryButton
import com.documind.ai.ui.components.DocumentCard
import com.documind.ai.ui.components.SectionHeader
import com.documind.ai.ui.components.StatusType

@Composable
fun HomeScreen(
    onNavigateToUpload: () -> Unit,
    onNavigateToDocument: (String) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Text(
            text = "DocuMind AI",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            text = "Document & Invoice Intelligence",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        DocuMindPrimaryButton(
            text = "Upload Document",
            onClick = onNavigateToUpload
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "Take a photo or select a PDF, JPG or PNG.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(48.dp))
        
        SectionHeader(title = "Recent Documents (Demo UI)")
        
        // Mocking a recent document since there's no backend connection yet
        DocumentCard(
            title = "Invoice #INV-1001 (Sample)",
            subtitle = "30 Sep 2026",
            amount = "₹1,180.00",
            status = "Information extracted",
            statusType = StatusType.SUCCESS
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        DocumentCard(
            title = "Unknown Receipt (Sample)",
            subtitle = "28 Sep 2026",
            amount = null,
            status = "Review required",
            statusType = StatusType.WARNING
        )
    }
}
