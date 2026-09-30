package com.documind.ai.ui.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.documind.ai.ui.components.DocuMindPrimaryButton
import com.documind.ai.ui.components.InformationRow
import com.documind.ai.ui.components.SectionHeader
import com.documind.ai.ui.components.StatusBadge
import com.documind.ai.ui.components.StatusType

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DocumentResultScreen(
    documentId: String,
    onBack: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Document Review") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp)
                .verticalScroll(rememberScrollState())
        ) {
            SectionHeader(title = "Document Type")
            
            Text(
                text = "INVOICE",
                style = MaterialTheme.typography.headlineMedium,
                color = MaterialTheme.colorScheme.primary
            )
            
            Spacer(modifier = Modifier.height(4.dp))
            
            Text(
                text = "Document identified as an invoice.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            StatusBadge(text = "Identification confidence: High", type = StatusType.BRAND)
            
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "This indicates how strongly the document matched invoice characteristics. It is not a government verification.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(32.dp))
            
            SectionHeader(title = "Information Found")
            StatusBadge(text = "Extracted from document", type = StatusType.INFO)
            
            Spacer(modifier = Modifier.height(16.dp))
            
            InformationRow(label = "Invoice Number", value = "INV-1001")
            InformationRow(label = "Invoice Date", value = "15 Sep 2026")
            
            Spacer(modifier = Modifier.height(16.dp))
            SectionHeader(title = "Seller")
            InformationRow(label = "Name", value = "ABC Technologies Pvt Ltd")
            InformationRow(label = "GSTIN", value = "29ABCDE1234F1Z5")
            
            Spacer(modifier = Modifier.height(16.dp))
            SectionHeader(title = "Amounts")
            InformationRow(label = "Taxable Value", value = "₹1,000.00")
            InformationRow(label = "CGST", value = "₹90.00")
            InformationRow(label = "SGST", value = "₹90.00")
            InformationRow(label = "Grand Total", value = "₹1,180.00")
            
            Spacer(modifier = Modifier.height(32.dp))
            
            DocuMindPrimaryButton(
                text = "Review Information",
                onClick = { /* Future feature */ }
            )
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}
