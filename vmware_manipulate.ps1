# Get the parameters needed
$vcenter="10.42.11.40"
$host_esx="10.42.11.25"
$user="administrator@vsphere.local"
$passwd="nx2Tech289!"
$Move_Templ="Win2k12R2"
$datastore="vmContainer1"

# Connect to the vCenter server
connect-viserver -force -server $vcenter -user $user -Password $passwd

# Get Move VMs from the vCenter
$Move_VM=Get-VM | where-object { $_.name -like 'Move*'}

# Delete the Move VMs
foreach ($vm in $Move_VM){
    if ($vm.PowerState -eq "PoweredOn"){
        Stop-VM -Kill $vm.name -confirm:$false | out-null
        echo "Stopped VM $vm"
     }
    Remove-VM -DeletePermanently $vm.name -confirm:$false | out-null
    echo "Removed VM $vm"
}


# Stop the PC environments and return to the last snapshot
$PC_vm=get-vm|where {$_.name -like 'PC*'}|select $_.name
foreach ($pc in $PC_vm){
    if ($pc.PowerState -eq "PoweredOn"){
        Stop-VM -Kill $pc.name -confirm:$false| out-null
        echo "Stopped VM $pc"
     }
    $snap = Get-Snapshot -VM $pc | Sort-Object -Property Created -Descending | Select -First 1
    Set-VM -VM $pc -SnapShot $snap -Confirm:$false| out-null
    echo "Reverted snapshot back for VM $pc"
    start-vm -VM $pc -RunAsync -confirm:$false| out-null
    echo "Starting VM $pc"
}

# Sleep 1 minute so the PCs can settle in
echo "Sleep 1 minute so the PCs can settle in"
sleep 60


# Create 15 new machine from the W2K12R2 template
for ($counter=1;$counter -le 15;$counter++){
    New-VM -Template $Move_Templ -Datastore $datastore -DiskStorageFormat Thin -Name Move-$counter -Resourcepool Move| out-null
    echo "Created VM Move-$counter"
    start-vm -VM Move-$counter -RunASync| out-null
    echo "Started VM Move-$counter"
}



# disconnect from vCenter
Disconnect-VIServer -server * -force -Confirm:$false