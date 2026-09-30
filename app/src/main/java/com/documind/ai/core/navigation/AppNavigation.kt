package com.documind.ai.core.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.documind.ai.ui.components.AppBottomNavigation
import com.documind.ai.ui.screens.documents.DocumentsScreen
import com.documind.ai.ui.screens.home.HomeScreen
import com.documind.ai.ui.screens.settings.SettingsScreen
import com.documind.ai.ui.screens.upload.UploadScreen
import com.documind.ai.ui.screens.processing.ProcessingScreen
import com.documind.ai.ui.screens.result.DocumentResultScreen
import com.documind.ai.ui.screens.about.AboutScreen

@Composable
fun AppNavigation(
    navController: NavHostController = rememberNavController()
) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    Scaffold(
        bottomBar = {
            // Only show Bottom Navigation on top level screens
            if (currentRoute == Screen.Home.route || currentRoute == Screen.Documents.route || currentRoute == Screen.Settings.route) {
                AppBottomNavigation(
                    currentRoute = currentRoute,
                    onNavigate = { screen ->
                        navController.navigate(screen.route) {
                            popUpTo(navController.graph.startDestinationId) {
                                saveState = true
                            }
                            launchSingleTop = true
                            restoreState = true
                        }
                    }
                )
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
