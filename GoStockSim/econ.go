package main

import (
	"bufio"
	"fmt"
	"math"
	"math/rand"
	"os"
	"os/exec"
	"runtime"
	"time"
)

const (
	initialPrice = 50.0
	maxBars      = 32
	chartHeight  = 20
	barChar      = "█"

	resetColor = "\033[0m"
	redColor   = "\033[31m"
	greenColor = "\033[32m"
)

type Game struct {
	prices       []float64
	money        float64
	holdings     int
	allTimeHigh  float64
	allTimeLow   float64
	bestNetWorth float64
}

func main() {
	rand.Seed(time.Now().UnixNano())
	game := Game{
		prices:       []float64{initialPrice},
		money:        100.0,
		holdings:     0,
		allTimeHigh:  initialPrice,
		allTimeLow:   initialPrice,
		bestNetWorth: 100.0, // initial funds
	}

	scanner := bufio.NewScanner(os.Stdin)

	for {
		game.render()

		fmt.Print("\nEnter ']' to buy, '#' to sell, anything else to wait: ")
		scanner.Scan()
		input := scanner.Text()

		switch input {
		case "]":
			game.buy()
		case "#":
			game.sell()
		default:
			game.updatePrice()
		}
	}
}

func (g *Game) updatePrice() {
	oldPrice := g.prices[len(g.prices)-1]
	var newPrice float64

	// 5% chance of spike or crash
	if rand.Float64() < 0.05 {
		spike := 0.4 + rand.Float64()*0.6 // 40% to 100%
		if rand.Float64() < 0.5 {
			newPrice = oldPrice * (1 + spike)
			fmt.Println("🚀 Market Rally! Price spiked!")
		} else {
			newPrice = oldPrice * (1 - spike)
			fmt.Println("💥 Market Crash! Price dropped!")
		}
	} else {
		// Biased random walk (more likely to go up)
		bias := 0.05
		change := (rand.Float64() - 0.45 + bias) * 0.5
		newPrice = oldPrice * (1 + change)
	}

	if newPrice < 1 {
		newPrice = 1
	}

	// Update rolling prices
	if len(g.prices) >= maxBars {
		g.prices = g.prices[1:]
	}
	g.prices = append(g.prices, newPrice)

	// Update high/low
	if newPrice > g.allTimeHigh {
		g.allTimeHigh = newPrice
	}
	if newPrice < g.allTimeLow {
		g.allTimeLow = newPrice
	}

	// Update best net worth
	g.updateBestNetWorth()
}

func (g *Game) buy() {
	current := g.prices[len(g.prices)-1]
	if g.money >= current {
		g.money -= current
		g.holdings++
		fmt.Println("✅ Bought 1 share at", fmt.Sprintf("$%.2f", current))
	} else {
		fmt.Println("❌ Not enough funds.")
	}
	g.updateBestNetWorth()
}

func (g *Game) sell() {
	if g.holdings > 0 {
		current := g.prices[len(g.prices)-1]
		g.money += current
		g.holdings--
		fmt.Println("✅ Sold 1 share at", fmt.Sprintf("$%.2f", current))
	} else {
		fmt.Println("❌ You don't own any shares.")
	}
	g.updateBestNetWorth()
}

func (g *Game) updateBestNetWorth() {
	currentPrice := g.prices[len(g.prices)-1]
	netWorth := g.money + float64(g.holdings)*currentPrice
	if netWorth > g.bestNetWorth {
		g.bestNetWorth = netWorth
	}
}

func (g *Game) render() {
	clearScreen()

	currentPrice := g.prices[len(g.prices)-1]

	fmt.Println("💰 Money:", fmt.Sprintf("$%.2f", g.money),
		"📦 Holdings:", g.holdings,
		"💎 Highest Net Worth:", fmt.Sprintf("$%.2f", g.bestNetWorth))
	fmt.Println("📈 Current Price:", fmt.Sprintf("$%.2f", currentPrice))
	fmt.Println("📊 All-Time High:", fmt.Sprintf("$%.2f", g.allTimeHigh),
		"| All-Time Low:", fmt.Sprintf("$%.2f", g.allTimeLow))
	fmt.Println("--- Stock Chart (Vertical) ---")

	max := maxInSlice(g.prices)

	for level := chartHeight; level >= 1; level-- {
		line := ""
		for i, price := range g.prices {
			height := int((price / max) * float64(chartHeight))
			color := resetColor
			if i > 0 {
				if price > g.prices[i-1] {
					color = greenColor
				} else if price < g.prices[i-1] {
					color = redColor
				}
			}
			if height >= level {
				line += color + barChar + resetColor + " "
			} else {
				line += "  "
			}
		}
		fmt.Printf("%2d | %s\n", level, line)
	}
	fmt.Println("    " + underline(len(g.prices)))
}

func underline(n int) string {
	line := ""
	for i := 0; i < n; i++ {
		line += "― "
	}
	return line
}

func maxInSlice(slice []float64) float64 {
	max := slice[0]
	for _, v := range slice {
		if v > max {
			max = v
		}
	}
	return math.Max(max, 1)
}

func clearScreen() {
	switch runtime.GOOS {
	case "windows":
		cmd := exec.Command("cmd", "/c", "cls")
		cmd.Stdout = os.Stdout
		cmd.Run()
	default:
		fmt.Print("\033[H\033[2J")
	}
}
