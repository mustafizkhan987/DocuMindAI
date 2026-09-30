package com.documind.ai.ui.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.documind.ai.ui.components.SectionHeader

@Composable
fun SettingsScreen(
    onNavigateToAbout: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Text(
            text = "Settings",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.onSurface
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        SectionHeader(title = "Application")
        SettingsItem(title = "Notifications", subtitle = "Manage alerts and updates")
        SettingsItem(title = "Appearance", subtitle = "Light, Dark, or System Default")
        SettingsItem(title = "Language", subtitle = "English")
        
        Spacer(modifier = Modifier.height(16.dp))
        
        SectionHeader(title = "Documents")
        SettingsItem(title = "Default document behavior", subtitle = "Auto-classify on upload")
        SettingsItem(title = "Storage information", subtitle = "12 MB used")
        
        Spacer(modifier = Modifier.height(16.dp))
        
        SectionHeader(title = "Privacy & Security")
        SettingsItem(title = "Privacy", subtitle = "Manage tracking and permissions")
        SettingsItem(title = "Data handling", subtitle = "On-device processing details")
        
        Spacer(modifier = Modifier.height(16.dp))
        
        SectionHeader(title = "About")
        SettingsItem(
            title = "About DocuMind AI", 
            subtitle = "Version, Terms, Privacy Policy",
            onClick = onNavigateToAbout
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsItem(
    title: String,
    subtitle: String,
    onClick: (() -> Unit)? = null
) {
    Card(
        onClick = { onClick?.invoke() },
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurface
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = subtitle,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
