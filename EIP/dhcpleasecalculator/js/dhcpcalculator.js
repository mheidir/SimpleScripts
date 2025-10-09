// DHCP LPS Estimator
const numClients = document.getElementById('numClients');
const projectedGrowth = document.getElementById('projectedGrowth');
const leaseHours = document.getElementById('leaseHours');
const leaseSeconds = document.getElementById('leaseSeconds');
const renewalHours = document.getElementById('renewalHours');
const renewalSeconds = document.getElementById('renewalSeconds');
const lpsNoGrowth = document.getElementById('lpsNoGrowth');
const lpsGrowth = document.getElementById('lpsGrowth');
const peakLps = document.getElementById('peakLps');

// DHCP Spike LPS
const numSpikeClients = document.getElementById('numSpikeClients');
const spikeRenewalPercent= document.getElementById('spikeRenewalPercentage');
const spikeMinutes = document.getElementById('spikeMinutes');
const spikeSeconds = document.getElementById('spikeSeconds');
const spikeLps = document.getElementById('spikeLps');

function calculateLps() {
    var clients = parseFloat(numClients.value), growth = parseFloat(projectedGrowth.value), leaseHrs = parseFloat(leaseHours.value), spikeClients = parseFloat(numSpikeClients.value);
    
    leaseSecs = leaseHrs * 3600;
    leaseSeconds.value = leaseSecs;
    
    renewalHours.value = leaseHrs / 2;
    renewalSeconds.value = leaseSecs / 2;
    
    lpsNoGrowth.value = (clients / (leaseSecs / 2)).toFixed(3);
    
    var spikeCl = clients + ((growth / 100) * clients);
    var lpsGrow = ((clients + ((growth / 100) * clients)) / (leaseSecs / 2));
    
    lpsGrowth.value = lpsGrow.toFixed(3);
    peakLps.value = (lpsGrow * 10).toFixed(3);
    
    calculateSpike(spikeCl);
    return;
}

function calculateSpike(spikeClients) {
    var spikePercent = parseFloat(spikeRenewalPercent.value), spikeMins = parseFloat(spikeMinutes.value);
    
    numSpikeClients.value = spikeClients.toFixed(0);
    
    var spikeSecs = spikeMins * 60;
    spikeSeconds.value = spikeSecs.toFixed(0);
    
    var spikeL = (spikeClients / spikeSecs) / 10;
    spikeLps.value = spikeL.toFixed(3);
    
    return;
}


numClients.addEventListener('input', function() {
    calculateLps();
    return;
});

projectedGrowth.addEventListener('input', function() {
    calculateLps();
    return;
});

leaseHours.addEventListener('input', function() {
    calculateLps();
    return;
});

spikeRenewalPercent.addEventListener('input', function () {
    calculateLps();
    return;
});

spikeMinutes.addEventListener('input', function() {
    calculateLps();
});

calculateLps();
