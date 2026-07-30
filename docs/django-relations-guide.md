# Django Relationships — Complete Study Guide

> For a Laravel dev learning Django. Every section maps a Django concept back to Eloquent.
> Examples use this project's models: `User`, `Wallet`, `Transaction`.

---

## 0. The One Rule That Fixes Half of Laravel-Dev Mistakes

In **Laravel** you name the foreign-key column yourself: `wallet_id`.
In **Django you name the _relationship_**, and Django creates the `_id` column for you.

```python
class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    #  ^ name it `wallet`, NOT `wallet_id`
```

This single field gives you **two** attributes:

| Access | Returns | Hits the DB? |
|---|---|---|
| `transaction.wallet` | the `Wallet` **object** | ✅ yes (a query, unless already loaded) |
| `transaction.wallet_id` | the raw **integer** FK | ❌ no — it's already on the row |

**Performance tip:** when you only need the id, use `transaction.wallet_id` — it avoids a query.
If you write `wallet_id = models.ForeignKey(...)`, Django creates a column called `wallet_id_id`. Don't.

---

## 1. The Four Relationship Types at a Glance

| Django | Eloquent equivalent | Column lives on | Cardinality |
|---|---|---|---|
| `ForeignKey` | `belongsTo` / `hasMany` | the "many" side | one → many |
| `OneToOneField` | `hasOne` / `belongsTo` | the side you declare it on | one → one |
| `ManyToManyField` | `belongsToMany` | a hidden join table | many ↔ many |
| `GenericForeignKey` | `morphTo` (polymorphic) | the model with the FK | any → many types |

---

## 2. ForeignKey — One-to-Many (the workhorse)

A `Wallet` has many `Transaction`s; each `Transaction` belongs to one `Wallet`.

### Define it (on the "many" side)

```python
class Transaction(models.Model):
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,      # see §6 for the choices
        related_name="transactions",   # how the reverse side is named
    )
    amount = models.BigIntegerField()
```

### Use it in queries

```python
# FORWARD (many -> one): from a transaction to its wallet
tx = Transaction.objects.get(pk=1)
tx.wallet            # the Wallet object   (1 query)
tx.wallet_id         # just the integer    (0 queries)

# REVERSE (one -> many): from a wallet to its transactions
wallet.transactions.all()                       # thanks to related_name
wallet.transactions.filter(amount__gt=1000)     # it's a full manager/queryset
wallet.transactions.count()

# WITHOUT related_name you'd be stuck with the ugly default:
wallet.transaction_set.all()    # <lowercase-model>_set
```

**Eloquent parallel:**
`$transaction->wallet` ≈ `tx.wallet`; `$wallet->transactions` ≈ `wallet.transactions.all()`.
Difference: in Django the reverse accessor is a **manager** — you can keep chaining `.filter()`, `.count()`, etc.

### Filtering across the relation (double-underscore = "join")

`__` is Django's "reach into the related table" operator (like Eloquent's `whereHas` / dot-paths):

```python
# All transactions belonging to a wallet whose balance is 0
Transaction.objects.filter(wallet__balance=0)

# All wallets that have at least one transaction over 1000
Wallet.objects.filter(transactions__amount__gt=1000).distinct()
```

---

## 3. OneToOneField — One-to-One

Your `User` has exactly one `Wallet`.

### Define it

```python
class User(AbstractUser):
    wallet = models.OneToOneField(
        Wallet,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="user",   # reverse: wallet.user
    )
```

A `OneToOneField` is a `ForeignKey` with `unique=True` baked in.

### Use it

```python
user.wallet          # forward: the Wallet   (like a belongsTo)
wallet.user          # reverse: the single User (NOT a queryset — one object)
```

Note the reverse side returns **one object**, not a manager. If none exists it raises
`RelatedObjectDoesNotExist`.

### Design note (which side holds the FK?)

The column lives on whichever model declares the field. You put it on `User`, so the
`user` table has a `wallet_id` column. Alternative: put it on `Wallet` pointing at `User`.
Rule of thumb: put it on the model that "can't exist without the other" or is created second.

---

## 4. ManyToManyField — Many-to-Many

Example: a `User` can attend many `GymClass`es, and each class has many users.

### Define it (on either side — pick the more natural owner)

```python
class GymClass(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(
        User,
        related_name="classes",
        blank=True,
    )
```

Django auto-creates a hidden **join table** (`gymclass_members`) with two FKs. No model needed.

### Use it

```python
gym_class.members.all()          # users in this class
user.classes.all()               # classes this user is in  (via related_name)

gym_class.members.add(user)      # attach   (Eloquent: $class->members()->attach($user))
gym_class.members.remove(user)   # detach
gym_class.members.set([u1, u2])  # sync     (Eloquent: ->sync([...]))
gym_class.members.clear()        # detach all
```

**Eloquent parallel:** `belongsToMany` + `attach/detach/sync/toggle`. Django's methods are
`add / remove / set / clear`.

### `through` — a custom join table (extra columns on the pivot)

When the relationship itself carries data (e.g. `joined_at`, `is_active`) — like Eloquent's
`withPivot` — define an explicit join model:

```python
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gym_class = models.ForeignKey(GymClass, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class GymClass(models.Model):
    members = models.ManyToManyField(User, through="Membership", related_name="classes")
```

With a `through` model you create rows via `Membership.objects.create(...)`
(you can't use `.add()` with extra required fields).

---

## 5. GenericForeignKey — Polymorphic ("morph")

Laravel's `morphTo` / `morphMany`. Use when one model relates to **several** other models.
Example: a `Comment` (or `Payment`) that can attach to a `Wallet`, an `Invoice`, or a `Subscription`.

Django implements this with the **`contenttypes`** framework (a registry of every model).

### Define it

```python
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Payment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # which model
    object_id = models.PositiveIntegerField()                                 # which row
    payable = GenericForeignKey("content_type", "object_id")                  # the magic accessor
    amount = models.BigIntegerField()
```

`content_type` + `object_id` together are Laravel's `payable_type` + `payable_id`.

### Use it

```python
payment.payable = some_invoice      # assign any model instance
payment.save()
payment.payable                     # -> the Invoice (or Wallet, or Subscription...)
```

### Reverse accessor (optional)

```python
from django.contrib.contenttypes.fields import GenericRelation

class Invoice(models.Model):
    payments = GenericRelation(Payment)

invoice.payments.all()
```

**Trade-off:** no DB-level foreign-key constraint (the DB can't enforce it), and queries are
harder to optimize. Use only when you truly need polymorphism; otherwise prefer explicit FKs.

---

## 6. `on_delete` — What Happens When the Parent Is Deleted

**Required** on every `ForeignKey`/`OneToOneField`. Laravel puts this in the migration
(`->onDelete('cascade')`); Django puts it on the model.

| Option | Effect | Use when |
|---|---|---|
| `CASCADE` | delete the children too | child is meaningless without parent (e.g. order items) |
| `PROTECT` | **block** the delete (raises `ProtectedError`) | must preserve history — **financial ledgers!** |
| `SET_NULL` | set FK to `NULL` (needs `null=True`) | child can outlive parent |
| `SET_DEFAULT` | set FK to its default | rare |
| `RESTRICT` | like PROTECT but allows cascades in the same batch | advanced |
| `DO_NOTHING` | nothing (you handle it in DB) | you have a DB-level rule |

**For `Transaction.wallet`, prefer `PROTECT`** — you never want to silently erase money history.

---

## 7. The N+1 Problem — The #1 ORM Interview Topic

### What it is

Looping over objects and touching a relation inside the loop fires **one query per row**:

```python
for tx in Transaction.objects.all():      # 1 query for the transactions
    print(tx.wallet.balance)              # + 1 query PER transaction  -> N+1 total
```

100 transactions = **101 queries**. Same trap as Eloquent without `with()`.

### The two fixes (know exactly when to use each)

| Tool | For which relations | How it works | Eloquent analog |
|---|---|---|---|
| `select_related` | `ForeignKey`, `OneToOne` (to-one) | SQL **JOIN**, one query | eager load a `belongsTo` |
| `prefetch_related` | `ManyToMany`, reverse FK (to-many), `GenericForeignKey` | **separate** query + joins in Python | eager load a `hasMany` |

```python
# to-ONE relation -> select_related (a JOIN)
for tx in Transaction.objects.select_related("wallet"):
    print(tx.wallet.balance)          # 1 query total

# to-MANY relation -> prefetch_related (2 queries total, joined in memory)
for wallet in Wallet.objects.prefetch_related("transactions"):
    for tx in wallet.transactions.all():
        print(tx.amount)              # 2 queries total, not N+1
```

**Rule of thumb:** *to-one → `select_related`; to-many → `prefetch_related`.*
You can chain and combine: `.select_related("wallet").prefetch_related("wallet__transactions")`.

### Advanced: shape the prefetch with `Prefetch`

```python
from django.db.models import Prefetch

Wallet.objects.prefetch_related(
    Prefetch("transactions", queryset=Transaction.objects.filter(amount__gt=0))
)
```

### How to actually catch N+1

- `django-debug-toolbar` shows query counts per request.
- In tests: `self.assertNumQueries(2): ...`
- `python manage.py shell` + `django.db.connection.queries` (with `DEBUG=True`).

---

## 8. QuerySets Are Lazy (a mental-model must-have)

A `QuerySet` doesn't hit the DB until you **evaluate** it (iterate, `list()`, `len()`, slice, `bool()`).
This is why you can keep chaining filters cheaply:

```python
qs = Transaction.objects.filter(amount__gt=0)   # no query yet
qs = qs.filter(wallet_id=5)                      # still no query
qs = qs.order_by("-id")                          # still no query
list(qs)                                          # NOW one SQL query runs
```

Related helpers you'll use constantly:

```python
Wallet.objects.get(pk=1)                 # exactly one row (raises if 0 or >1)
Wallet.objects.filter(balance=0)         # a queryset (0..N rows)
Wallet.objects.first() / .last()
Wallet.objects.exists()                  # cheap existence check
Transaction.objects.count()
Wallet.objects.values("id", "balance")   # dicts instead of model instances
```

---

## 9. `F()` and `select_for_update` — Safe Concurrent Updates (money!)

Updating a balance with read-modify-write in Python is a **race condition**:

```python
wallet.balance = wallet.balance + 100     # BAD under concurrency (lost updates)
wallet.save()
```

Do the arithmetic **in the database** with `F()`:

```python
from django.db.models import F
Wallet.objects.filter(pk=w.id).update(balance=F("balance") + 100)   # atomic at DB level
```

For read-then-write inside a transaction, lock the row:

```python
from django.db import transaction
with transaction.atomic():
    wallet = Wallet.objects.select_for_update().get(pk=w.id)   # locks the row
    # ... compute, write ledger row + update balance together ...
```

This is the senior-level answer to "how do you prevent double-spend on a wallet."

---

## 10. Quick Reference — Cheat Sheet

```python
# DEFINE
fk   = models.ForeignKey(Parent, on_delete=models.PROTECT, related_name="children")
o2o  = models.OneToOneField(Other, on_delete=models.CASCADE, related_name="owner")
m2m  = models.ManyToManyField(Tag, related_name="items", blank=True)

# TRAVERSE
child.parent          child.parent_id        parent.children.all()
a.other               b.owner
item.tags.all()       item.tags.add(t)       item.tags.set([...])

# FILTER ACROSS RELATIONS  (__ = join)
Model.objects.filter(parent__name="x")
Model.objects.filter(children__amount__gt=100).distinct()

# AVOID N+1
.select_related("fk_or_o2o")            # to-one  -> JOIN
.prefetch_related("m2m_or_reverse_fk")  # to-many -> 2nd query

# MIGRATIONS (after ANY model change)
python manage.py makemigrations
python manage.py migrate
```

---

## 11. Interview One-Liners (say these and sound senior)

- *"Name the field after the relationship, not the column — Django appends `_id` itself, and I get both `obj.fk` and `obj.fk_id`."*
- *"`select_related` for to-one (a JOIN), `prefetch_related` for to-many (a second query joined in Python) — that's how I kill N+1."*
- *"QuerySets are lazy; they don't touch the DB until evaluated, so chaining filters is free."*
- *"For a financial ledger I use `on_delete=PROTECT` so history can't be silently deleted."*
- *"Concurrent balance updates use `F()` expressions or `select_for_update()` inside `transaction.atomic()` to avoid race conditions."*
- *"Polymorphic relations use the `contenttypes` framework — `content_type` + `object_id` + `GenericForeignKey`, the equivalent of Laravel's morphTo."*
```
