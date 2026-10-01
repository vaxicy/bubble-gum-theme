// Bubble Gum - a tiny gumball machine you can crank from the terminal.
import { clamp, mixHex } from "./palette.js";

const FLAVORS = {
  strawberry: "#FB83ED",
  blueberry: "#7B7BD6",
  mint: "#8E9A56",
  lemon: "#C2753C",
};

const MAX_GUMBALLS = 24;

export class GumballMachine {
  constructor(capacity = MAX_GUMBALLS, price = 0.25) {
    this.capacity = capacity;
    this.price = price;
    this.coins = 0;
    this.gumballs = [];
  }

  stock(flavor, count = 6) {
    for (let i = 0; i < clamp(count, 0, this.capacity); i += 1) {
      this.gumballs.push(flavor);
    }
    return this.gumballs.length;
  }

  insert(amount) {
    if (amount <= 0) {
      throw new RangeError(`amount must be positive, got ${amount}`);
    }
    this.coins += amount;
    return this.coins;
  }

  crank() {
    if (this.coins < this.price) {
      return { ok: false, reason: "insert a coin first" };
    }
    if (this.gumballs.length === 0) {
      return { ok: false, reason: "out of stock" };
    }
    this.coins -= this.price;
    const flavor = this.gumballs.shift();
    return { ok: true, flavor, color: FLAVORS[flavor], change: this.coins };
  }
}

export function describe(machine) {
  const tint = mixHex(FLAVORS.strawberry, "#FFFFFF", 0.35);
  return `gumballs: ${machine.gumballs.length} of ${machine.capacity} (${tint})`;
}

const machine = new GumballMachine(12, 0.25);
machine.stock("strawberry", 4);
machine.stock("blueberry", 3);
machine.insert(1);

console.log(describe(machine));
console.log(machine.crank());
