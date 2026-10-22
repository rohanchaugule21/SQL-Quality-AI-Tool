-- Test Stored Procedure with Issues
CREATE PROCEDURE usp_GetCustomerReport
    @StartDate DATETIME,
    @EndDate DATETIME
AS
BEGIN
    -- Missing SET NOCOUNT ON
    
    DECLARE @OrderCount INT
    
    -- Issue 1: SELECT *
    SELECT * 
    INTO #TempOrders
    FROM Orders o WITH (NOLOCK)  -- Issue 2: NOLOCK
    WHERE YEAR(OrderDate) = 2026  -- Issue 3: Non-sargable
        AND CustomerID IN (
            SELECT CustomerID 
            FROM Customers 
            WHERE City = 'London'
        )
    
    -- Issue 4: Cursor usage
    DECLARE order_cursor CURSOR FOR
        SELECT OrderID, OrderDate, TotalAmount
        FROM #TempOrders
    
    OPEN order_cursor
    
    FETCH NEXT FROM order_cursor
    INTO @OrderID, @OrderDate, @TotalAmount
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Process each order
        PRINT 'Processing Order: ' + CAST(@OrderID AS VARCHAR(10))
        
        FETCH NEXT FROM order_cursor
        INTO @OrderID, @OrderDate, @TotalAmount
    END
    
    CLOSE order_cursor
    DEALLOCATE order_cursor
    
    DROP TABLE #TempOrders
END
GO