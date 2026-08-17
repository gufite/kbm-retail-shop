import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate
from frappe.utils.synchronization import filelock

from retail_shop.utils.commission import get_commission_earned, get_commission_paid


class CommissionPayment(Document):
	def validate(self):
		if getdate(self.from_date) > getdate(self.to_date):
			frappe.throw(_("From Date cannot be after To Date."))

		self.commission_earned = get_commission_earned(self.electrician, self.from_date, self.to_date)

		if flt(self.amount_paid) <= 0:
			frappe.throw(_("Amount Paid must be greater than zero."))

		# Soft check only here so a draft shows a helpful estimate; the
		# authoritative, race-safe check is in before_submit (see below),
		# which is what actually locks in the payout.
		self._check_outstanding()

	def before_submit(self):
		# Two concurrent submissions for the same electrician could otherwise
		# both read the same "outstanding" figure before either commits, and
		# both pass the check — paying the same commission twice. Serialize
		# per electrician and hold the lock through on_submit's explicit
		# commit, so the next waiter's check only proceeds once this
		# payment is actually durable. A plain file lock (rather than a
		# distributed one) is proportionate here: single-server, one-shop
		# deployment with no realistic multi-node concurrency.
		self.flags._commission_lock = filelock(f"commission-payment-{self.electrician}", timeout=10)
		self.flags._commission_lock.__enter__()
		try:
			self._check_outstanding(exclude_self=True)
		except Exception:
			self._release_commission_lock()
			raise

	def on_submit(self):
		# db_update() (which writes this doc's own docstatus=1 row) already
		# ran by this point — committing now, before releasing the lock,
		# is what makes the next waiter's check actually see this payment.
		if self.flags.get("_commission_lock"):
			frappe.db.commit()
			self._release_commission_lock()

	def _release_commission_lock(self):
		lock = self.flags.get("_commission_lock")
		if lock:
			lock.__exit__(None, None, None)
			self.flags._commission_lock = None

	def _check_outstanding(self, exclude_self=False):
		already_paid = get_commission_paid(
			self.electrician, self.from_date, self.to_date, exclude=self.name if exclude_self else None
		)
		outstanding = flt(self.commission_earned) - flt(already_paid)
		if flt(self.amount_paid) > outstanding:
			frappe.throw(
				_("Amount Paid ({0}) cannot exceed the commission outstanding for this period ({1}).").format(
					frappe.format_value(self.amount_paid, {"fieldtype": "Currency"}),
					frappe.format_value(outstanding, {"fieldtype": "Currency"}),
				)
			)
