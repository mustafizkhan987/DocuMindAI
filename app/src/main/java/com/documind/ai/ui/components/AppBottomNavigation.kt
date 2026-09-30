package com.documind.ai.ui.components

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Description
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import com.documind.ai.core.navigation.Screen

@Composable
fun AppBottomNavigation(
    currentRoute: String?,
    onNavigate: (Screen) -> Unit
) {
    val items = listOf(
        Screen.Home,
        Screen.Documents,
        Screen.Settings
    )

    NavigationBar(
        containerColor = MaterialTheme.colorScheme.surface,
        contentColor = MaterialTheme.colorScheme.onSurface
    ) {
        items.forEach { screen ->
            val selected = currentRoute == screen.route
            val icon = when (screen) {
                Screen.Home -> Icons.Default.Home
                Screen.Documents -> Icons.Default.Description
                Screen.Settings -> Icons.Default.Settings
                else -> Icons.Default.Home // Fallback for exhaustiveness
            }

            NavigationBarItem(
                selected = selected,
                onClick = { onNavigate(screen) },
                icon = { Icon(imageVector = icon, contentDescription = screen.title) },
                label = { Text(screen.title) },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = MaterialTheme.colorScheme.primary,
                    selectedTextColor = MaterialTheme.colorScheme.primary,
                    indicatorColor = MaterialTheme.colorScheme.surfaceVariant,
                    unselectedIconColor = MaterialTheme.colorScheme.onSurfaceVariant,
                    unselectedTextColor = MaterialTheme.colorScheme.onSurfaceVariant
                )
            )
        }
    }
}
