/**
 * OKX量化交易系统 - 前端主逻辑
 */

// WebSocket连接
let socket = null;
let pnlChart = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initWebSocket();
    loadInitialData();
    updateTime();
    setInterval(updateTime, 1000);
});

/**
 * 初始化WebSocket连接
 */
function initWebSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('WebSocket已连接');
        updateNetworkStatus({ status: 'connected', latency: 0 });
    });
    
    socket.on('disconnect', function() {
        console.log('WebSocket已断开');
        updateNetworkStatus({ status: 'disconnected' });
    });
    
    // 接收持仓更新
    socket.on('positions_update', function(positions) {
        updatePositions(positions);
    });
    
    // 接收余额更新
    socket.on('balance_update', function(balance) {
        updateBalance(balance);
    });
    
    // 接收网络状态
    socket.on('network_status', function(status) {
        updateNetworkStatus(status);
    });
}

/**
 * 加载初始数据
 */
async function loadInitialData() {
    await Promise.all([
        loadOrders(),
        loadStatistics(),
        loadBalanceHistory()
    ]);
}

/**
 * 更新时间显示
 */
function updateTime() {
    const now = new Date();
    const timeStr = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('current-time').textContent = timeStr;
}

/**
 * 检查网络状态
 */
async function checkNetwork() {
    try {
        const response = await fetch('/api/network');
        const status = await response.json();
        updateNetworkStatus(status);
    } catch (error) {
        console.error('检查网络失败:', error);
    }
}

/**
 * 更新网络状态显示
 */
function updateNetworkStatus(status) {
    const statusEl = document.getElementById('connection-status');
    const latencyEl = document.getElementById('latency');
    const lastUpdateEl = document.getElementById('last-update');
    
    if (status.status === 'connected') {
        statusEl.textContent = '已连接';
        statusEl.className = 'status-badge connected';
        latencyEl.textContent = `${status.latency || 0} ms`;
    } else {
        statusEl.textContent = '未连接';
        statusEl.className = 'status-badge disconnected';
        latencyEl.textContent = '-- ms';
    }
    
    lastUpdateEl.textContent = new Date().toLocaleTimeString('zh-CN');
}

/**
 * 更新余额显示
 */
function updateBalance(balance) {
    if (!balance) return;
    
    document.getElementById('total-balance').textContent = 
        `${(balance.total || 0).toFixed(2)} USDT`;
    
    document.getElementById('available-balance').textContent = 
        `${(balance.free || 0).toFixed(2)} USDT`;
}

/**
 * 更新持仓显示
 */
function updatePositions(positions) {
    const tbody = document.getElementById('positions-body');
    
    if (!positions || positions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="no-data">暂无持仓</td></tr>';
        
        // 更新未实现盈亏为0
        document.getElementById('unrealized-pnl').textContent = '0.00 USDT';
        document.getElementById('unrealized-pnl').className = 'balance-value';
        return;
    }
    
    let totalUnrealizedPnl = 0;
    
    tbody.innerHTML = positions.map(pos => {
        const pnl = pos.unrealized_pnl || 0;
        totalUnrealizedPnl += pnl;
        
        const pnlClass = pnl >= 0 ? 'positive' : 'negative';
        const sideClass = pos.side === 'long' ? 'side-long' : 'side-short';
        const sideText = pos.side === 'long' ? '做多' : '做空';
        
        // 计算收益率
        const margin = pos.margin || 1;
        const returnRate = margin > 0 ? (pnl / margin * 100) : 0;
        
        return `
            <tr>
                <td>${pos.symbol || '--'}</td>
                <td class="${sideClass}">${sideText}</td>
                <td>${(pos.size || 0).toFixed(4)}</td>
                <td>${pos.leverage || 0}x</td>
                <td>${(pos.entry_price || 0).toFixed(2)}</td>
                <td>${(pos.current_price || 0).toFixed(2)}</td>
                <td class="${pnlClass}">${pnl.toFixed(2)} USDT</td>
                <td class="${pnlClass}">${returnRate.toFixed(2)}%</td>
            </tr>
        `;
    }).join('');
    
    // 更新未实现盈亏
    const pnlEl = document.getElementById('unrealized-pnl');
    pnlEl.textContent = `${totalUnrealizedPnl.toFixed(2)} USDT`;
    pnlEl.className = `balance-value ${totalUnrealizedPnl >= 0 ? 'positive' : 'negative'}`;
}

/**
 * 加载历史订单
 */
async function loadOrders() {
    const period = document.getElementById('filter-period').value;
    const limit = document.getElementById('filter-limit').value;
    
    try {
        const response = await fetch(`/api/orders?period=${period}&limit=${limit}`);
        const orders = await response.json();
        renderOrders(orders);
    } catch (error) {
        console.error('加载订单失败:', error);
    }
}

/**
 * 渲染订单列表
 */
function renderOrders(orders) {
    const tbody = document.getElementById('orders-body');
    
    if (!orders || orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="no-data">暂无交易记录</td></tr>';
        return;
    }
    
    tbody.innerHTML = orders.map(order => {
        const pnl = order.pnl || 0;
        const pnlClass = pnl >= 0 ? 'positive' : 'negative';
        const sideClass = order.side === 'long' ? 'side-long' : 'side-short';
        const sideText = order.side === 'long' ? '做多' : '做空';
        
        // 计算收益率（简化）
        const margin = (order.size * order.price) / (order.leverage || 1);
        const returnRate = margin > 0 ? (pnl / margin * 100) : 0;
        
        // 格式化时间
        const closeTime = order.close_time ? 
            new Date(order.close_time).toLocaleString('zh-CN') : '--';
        
        return `
            <tr>
                <td>${closeTime}</td>
                <td>${order.symbol || '--'}</td>
                <td class="${sideClass}">${sideText}</td>
                <td>${(order.size || 0).toFixed(4)}</td>
                <td>${(order.price || 0).toFixed(2)}</td>
                <td>${(order.price || 0).toFixed(2)}</td>
                <td>${order.leverage || 0}x</td>
                <td>${(order.fee || 0).toFixed(2)}</td>
                <td class="${pnlClass}">${pnl.toFixed(2)}</td>
                <td class="${pnlClass}">${returnRate.toFixed(2)}%</td>
            </tr>
        `;
    }).join('');
}

/**
 * 加载统计数据
 */
async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const stats = await response.json();
        
        const totalPnl = stats.total_pnl || 0;
        const pnlEl = document.getElementById('total-pnl');
        pnlEl.textContent = `${totalPnl.toFixed(2)} USDT`;
        pnlEl.className = `balance-value ${totalPnl >= 0 ? 'positive' : 'negative'}`;
    } catch (error) {
        console.error('加载统计失败:', error);
    }
}

/**
 * 加载余额历史并绘制图表
 */
async function loadBalanceHistory() {
    try {
        const response = await fetch('/api/balance/history?limit=100');
        const history = await response.json();
        
        if (history && history.length > 0) {
            renderPnlChart(history);
        }
    } catch (error) {
        console.error('加载余额历史失败:', error);
    }
}

/**
 * 渲染收益图表
 */
function renderPnlChart(history) {
    const ctx = document.getElementById('pnl-chart').getContext('2d');
    
    // 反转数组使时间从左到右
    const reversed = [...history].reverse();
    
    const labels = reversed.map(item => {
        const date = new Date(item.timestamp);
        return date.toLocaleString('zh-CN', { 
            month: '2-digit', 
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    });
    
    const data = reversed.map(item => item.total_equity || item.total_balance || 0);
    
    if (pnlChart) {
        pnlChart.destroy();
    }
    
    pnlChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '账户权益',
                data: data,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toFixed(2) + ' USDT';
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxTicksLimit: 10
                    }
                },
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}
