---
id: android_jetpack_compose
version: 1.0.0
owners:
  - mobile_engineer
tags:
  - android
  - compose
  - kotlin
  - mobile
when_to_use: "When building Android features with Jetpack Compose, designing Android UI architecture, or implementing MVVM with StateFlow."
inputs:
  - feature requirements
  - Android min SDK
  - existing architecture pattern
outputs:
  - Compose UI components
  - ViewModel with StateFlow
  - Repository layer
  - unit tests
---

> "State flows down, events flow up. That's the whole architecture."

## MVVM + UiState Pattern

```kotlin
// UiState — single sealed class drives all UI states
data class OrdersUiState(
    val orders: List<Order> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
)

// ViewModel
@HiltViewModel
class OrdersViewModel @Inject constructor(
    private val repository: OrderRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(OrdersUiState())
    val uiState: StateFlow<OrdersUiState> = _uiState.asStateFlow()

    init { loadOrders() }

    fun loadOrders() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            repository.fetchOrders()
                .onSuccess { orders ->
                    _uiState.update { it.copy(orders = orders, isLoading = false) }
                }
                .onFailure { e ->
                    _uiState.update { it.copy(error = e.message, isLoading = false) }
                }
        }
    }
}

// Composable Screen
@Composable
fun OrdersScreen(
    viewModel: OrdersViewModel = hiltViewModel(),
    onOrderClick: (Order) -> Unit,
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when {
        uiState.isLoading -> Box(Modifier.fillMaxSize()) {
            CircularProgressIndicator(Modifier.align(Alignment.Center))
        }
        uiState.error != null -> ErrorScreen(message = uiState.error!!)
        else -> LazyColumn {
            items(uiState.orders, key = { it.id }) { order ->
                OrderItem(order = order, onClick = { onOrderClick(order) })
            }
        }
    }
}
```

## Anti-Patterns

- **`collectAsState()` without lifecycle** — use `collectAsStateWithLifecycle()` to stop collection when backgrounded
- **Business logic in Composables** — Composables are display-only; logic belongs in ViewModel
- **Mutable state in Composable** — use `remember` only for UI-local state (focus, animation)
- **`LaunchedEffect` for one-shot events** — use `Channel`/`SharedFlow` for navigation and snackbar events

## Validation Checklist

- [ ] Single UiState data class drives all screen states
- [ ] StateFlow exposed (not MutableStateFlow) from ViewModel
- [ ] `collectAsStateWithLifecycle()` used (not `collectAsState()`)
- [ ] Side effects (navigation, snackbar) via `Channel` not `StateFlow`
- [ ] ViewModel injected with Hilt — no `viewModel { }` direct instantiation in tests
