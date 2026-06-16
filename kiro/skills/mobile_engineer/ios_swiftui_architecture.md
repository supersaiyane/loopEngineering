---
id: ios_swiftui_architecture
version: 1.0.0
owners:
  - mobile_engineer
tags:
  - ios
  - swiftui
  - swift
  - mobile
when_to_use: "When building iOS features with SwiftUI, designing iOS app architecture, or implementing MVVM patterns for Swift applications."
inputs:
  - feature requirements
  - iOS target version
  - existing architecture pattern
outputs:
  - SwiftUI views
  - ViewModel
  - repository layer
  - unit tests
---

> "SwiftUI is declarative. Your architecture should be too."

## MVVM + Repository Pattern

```swift
// MARK: — Model
struct Order: Identifiable, Decodable {
    let id: UUID
    let customerName: String
    let amount: Decimal
    let status: OrderStatus
}

enum OrderStatus: String, Decodable {
    case pending, completed, cancelled
}

// MARK: — Repository (data layer, testable)
protocol OrderRepository {
    func fetchOrders() async throws -> [Order]
    func updateStatus(id: UUID, status: OrderStatus) async throws
}

final class RemoteOrderRepository: OrderRepository {
    private let apiClient: APIClient

    func fetchOrders() async throws -> [Order] {
        try await apiClient.get("/orders")
    }
    func updateStatus(id: UUID, status: OrderStatus) async throws {
        try await apiClient.patch("/orders/\(id)", body: ["status": status.rawValue])
    }
}

// MARK: — ViewModel (@Observable in iOS 17+)
@Observable
final class OrdersViewModel {
    private(set) var orders: [Order] = []
    private(set) var isLoading = false
    private(set) var error: Error?
    private let repository: OrderRepository

    init(repository: OrderRepository = RemoteOrderRepository()) {
        self.repository = repository
    }

    func loadOrders() async {
        isLoading = true
        error = nil
        do {
            orders = try await repository.fetchOrders()
        } catch {
            self.error = error
        }
        isLoading = false
    }
}

// MARK: — View
struct OrdersView: View {
    @State private var viewModel = OrdersViewModel()

    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading {
                    ProgressView()
                } else if let error = viewModel.error {
                    ContentUnavailableView(error.localizedDescription, systemImage: "exclamationmark.triangle")
                } else {
                    List(viewModel.orders) { order in
                        OrderRow(order: order)
                    }
                }
            }
            .navigationTitle("Orders")
        }
        .task { await viewModel.loadOrders() }
    }
}
```

## Anti-Patterns

- **Business logic in Views** — move to ViewModel; Views are display-only
- **Singletons for state** — use `@Observable` injected via `.environment()`
- **Force unwraps in production** — use guard/if-let; crash = bad UX
- **Synchronous network on main thread** — always `async`/`await` with `.task`

## Validation Checklist

- [ ] ViewModel is injected (not instantiated inside View)
- [ ] Repository protocol exists — enables mock injection in tests
- [ ] All async work uses `async/await`, not callbacks
- [ ] Errors are shown to user, not silently swallowed
- [ ] Unit tests use a `MockOrderRepository`
