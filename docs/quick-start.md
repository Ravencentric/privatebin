For quick, single interactions with PrivateBin, use the top-level convenience functions: 

- [`privatebin.get`][privatebin.get]
- [`privatebin.create`][privatebin.create]
- [`privatebin.delete`][privatebin.delete]

They offer a convenient way to quickly interact with PrivateBin
without setting up a [`PrivateBin`][privatebin.PrivateBin] client.
Each function automatically creates a temporary client for its operation and then releases it.

Because they create a new client each time, these functions are less efficient and performant
if you are performing many operations in a row against the same PrivateBin instance.
For more complex workflows, or when you need direct control over network requests
(for example, to configure timeouts, proxies, or custom headers), it is more efficient
and flexible to create and reuse a [`PrivateBin`][privatebin.PrivateBin] client instance directly.

---

::: privatebin.get
::: privatebin.create
::: privatebin.delete
