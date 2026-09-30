package com.documind.ai.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.documind.ai.ui.screens.HomeScreen
import com.documind.ai.ui.screens.DocumentsScreen
import com.documind.ai.ui.screens.SettingsScreen
import com.documind.ai.ui.screens.UploadScreen
import com.documind.ai.ui.screens.ProcessingScreen
import com.documind.ai.ui.screens.DocumentResultScreen
import com.documind.ai.ui.screens.AboutScreen

@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    
    val bottomNavItems = listOf(
        Screen.Home,
        Screen.Documents,
        Screen.Settings
    )

    Scaffold(
        bottomBar = {
            val navBackStackEntry by navController.currentBackStackEntryAsState()
            val currentDestination = navBackStackEntry?.destination
            
            // Only show bottom bar on top-level screens
            if (currentDestination?.route in bottomNavItems.map { it.route }) {
                NavigationBar {
                    bottomNavItems.forEach { screen ->
                        NavigationBarItem(
                            icon = { Icon(screen.icon, contentDescription = screen.title) },
                            label = { Text(screen.title) },
                            selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true,
                            onClick = {
                                navController.navigate(screen.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            }
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Home.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Home.route) {
                HomeScreen(
                    onNavigateToUpload = { navController.navigate(Screen.Upload.route) },
                    onNavigateToDocument = { docId -> navController.navigate(Screen.DocumentResult.createRoute(docId)) }
                )
            }
            composable(Screen.Documents.route) {
                DocumentsScreen(
                    onNavigateToUpload = { navController.navigate(Screen.Upload.route) },
                    onNavigateToDocument = { docId -> navController.navigate(Screen.DocumentResult.createRoute(docId)) }
                )
            }
            composable(Screen.Settings.route) {
                SettingsScreen(
                    onNavigateToAbout = { navController.navigate(Screen.About.route) }
                )
            }
            composable(Screen.Upload.route) {
                UploadScreen(
                    onBack = { navController.popBackStack() },
                    onUploadComplete = { docId -> 
                        navController.navigate(Screen.Processing.createRoute(docId)) {
                            popUpTo(Screen.Home.route)
                        }
                    }
                )
            }
            composable(Screen.Processing.route) { backStackEntry ->
                val documentId = backStackEntry.arguments?.getString("documentId") ?: ""
                ProcessingScreen(
                    documentId = documentId,
                    onProcessingComplete = { 
                        navController.navigate(Screen.DocumentResult.createRoute(documentId)) {
                            popUpTo(Screen.Home.route)
                        }
                    }
                )
            }
            composable(Screen.DocumentResult.route) { backStackEntry ->
                val documentId = backStackEntry.arguments?.getString("documentId") ?: ""
                DocumentResultScreen(
                    documentId = documentId,
                    onBack = { navController.navigate(Screen.Home.route) { popUpTo(0) } }
                )
            }
            composable(Screen.About.route) {
                AboutScreen(
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}
