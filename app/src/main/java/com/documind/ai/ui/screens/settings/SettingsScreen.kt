package com.documind.ai.ui.screens.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.NetworkCheck
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.documind.ai.network.NetworkConfig

@Composable
fun SettingsScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0F172A))
            .padding(16.dp)
    ) {
        Text(
            text = "Settings",
            color = Color.White,
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Application configuration & environment info",
            color = Color(0xFF94A3B8),
            fontSize = 13.sp
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Application Info Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1E293B))
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Info,
                        contentDescription = null,
                        tint = Color(0xFF2563EB)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = "App Information",
                        color = Color.White,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                Spacer(modifier = Modifier.height(12.dp))
                Text(text = "App Name: DocuMind AI", color = Color(0xFF94A3B8), fontSize = 14.sp)
                Text(text = "Version: 1.0 (Task 3 Foundation)", color = Color(0xFF94A3B8), fontSize = 14.sp)
                Text(text = "Platform: Android (Kotlin + Compose)", color = Color(0xFF94A3B8), fontSize = 14.sp)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // API Environment Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1E293B))
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.NetworkCheck,
                        contentDescription = null,
                        tint = Color(0xFF00E676)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = "Network Configuration",
                        color = Color.White,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                Spacer(modifier = Modifier.height(12.dp))
                Text(text = "Emulator URL: ${NetworkConfig.BASE_URL_EMULATOR}", color = Color(0xFF94A3B8), fontSize = 14.sp)
                Text(text = "Localhost URL: ${NetworkConfig.BASE_URL_LOCALHOST}", color = Color(0xFF94A3B8), fontSize = 14.sp)
                Text(text = "Target Endpoint: GET /api/v1/health", color = Color(0xFF94A3B8), fontSize = 14.sp)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Security Info Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1E293B))
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Lock,
                        contentDescription = null,
                        tint = Color(0xFFFFB74D)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = "Security & Privacy",
                        color = Color.White,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                Spacer(modifier = Modifier.height(12.dp))
                Text(text = "Zero Hardcoded Secrets: Verified", color = Color(0xFF94A3B8), fontSize = 14.sp)
                Text(text = "Authentication: Prepared for Task 31+", color = Color(0xFF94A3B8), fontSize = 14.sp)
            }
        }
    }
}
