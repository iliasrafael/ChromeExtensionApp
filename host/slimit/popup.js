function calc(){}

calc.prototype = {
	error:function(txt)
	{
		$('.error').text(txt);
		$('.error').fadeIn(500);
		if(this.errorInterval)
			clearInterval(this.errorInterval)
		this.errorInterval = setInterval(function(){
			$('.error').fadeOut(500);
		}, 1500)
	},
	
	lc:function()
	{
		return $('.el:last-child');
	},
	
	answer: function()
	{
		function setNumbers(num)
		{
			var new_num = '';
			var num_str = num.toString();
			for(var i in num_str)
				new_num += "<span class='number'>"+num_str[i]+"</span>";
			
			return new_num;
		}
		$('.action').each(function(k, v){
			if($(v).text() == '*' || $(v).text() == '/' || $(v).text() == '%')
			{
				var next = $(v).next();
				var prev = $(v).prev();
				if(next.text().toString() && prev.text().toString())
				{
					if($(v).text() ==  '*')
					{
						var num = parseFloat(prev.text()) *  parseFloat(next.text());
						$(v).next().remove();
						$(v).prev().html(setNumbers(num));
						$(v).remove();
					}
					
					if($(v).text() ==  '/')
					{
						var num = parseFloat(prev.text()) /  parseFloat(next.text());
						$(v).next().remove();
						$(v).prev().html(setNumbers(num));
						$(v).remove();
					}
					if($(v).text() ==  '%')
					{
						var num = (parseFloat(prev.text()) *  parseFloat(next.text()))/100;
						$(v).next().remove();
						$(v).prev().html(setNumbers(num));
						$(v).remove();
					}
				}
			}
			
		})
		$('.action').each(function(k, v){
			if($(v).text() == '+' || $(v).text() == '-')
			{
				var next = $(v).next();
				var prev = $(v).prev();
				if(next.text().toString() && prev.text().toString())
				{
					if($(v).text() ==  '+')
					{
						var num = parseFloat(prev.text()) +  parseFloat(next.text());
						$(v).next().remove();
						$(v).prev().html(setNumbers(num));
						$(v).remove();
					}
					if($(v).text() ==  '-')
					{
						var num = parseFloat(prev.text()) -  parseFloat(next.text());
						$(v).next().remove();
						$(v).prev().html(setNumbers(num));
						$(v).remove();
					}
				}
			}
		})
		this.init();
	},
	
	addNumber: function(number)
	{
		if(this.lc().hasClass('bn'))
		{
			if(this.lc()[0].childNodes.length >= 20)
				this.error('Maximum number of digits (20) exceeded')
			else
				this.lc().append('<span class="number">' + number + '</span>');
		}
		else
		{
			$('.textarea').append('<div class="el bn" ></div>');
			this.lc().append('<span class="number">' + number + '</span>');
		}
		this.init();
	},
	
	addAction: function(action)
	{
		if(this.lc().hasClass('action'))
			this.lc().remove();	
		
		if(this.lc().hasClass('bn') && $(this.lc()[0].lastChild).hasClass('pointAction'))
			this.addNumber(0);
		
		if(this.lc().length)
			$('.textarea').append('<span class="el action">' + action + '</span>');
		this.init();
	},
	
	clear: function()
	{
		$('.textarea').empty();
		this.init();
	},
	
	init: function()
	{
		if($('.number, .action').length > 13)
		{
			$('.el').css('font-size' , '2em')
		}else
		{
			$('.el').css('font-size' , '3em')
		}
		$('.textarea').scrollTop($('.textarea').height())
	},
	
	pointAction:function()
	{
		var number;
		
		if(this.lc().hasClass('bn'))
			number = this.lc();
		else if(this.lc().prev().hasClass('bn'))
			number = this.lc().prev();
		else
			return false;
		
		if(number.find('.pointAction').length)
			return false;
		
		number.append('<span class="numAction pointAction">.</span>');
		
		this.init();
	},
	
	pmAction: function()
	{
		var number;
		
		if(this.lc().hasClass('bn'))
			number = this.lc();
		else if(this.lc().prev().hasClass('bn'))
			number = this.lc().prev();
		else
			return false;
		
		
		if(number.find('.pmAction').length)
			number.find('.pmAction').remove()
		else
			number.find('.number:first-child').before('<span class="numAction pmAction">-</span>');
		
		
		this.init();
	},
	
	removeEl: function()
	{
		if($($('.textarea')[0].lastChild).hasClass('bn'))
		{
			$($($('.textarea')[0].lastChild)[0].lastChild).remove();
			if($($('.textarea')[0].lastChild).children().length == 0)
				$($('.textarea')[0].lastChild).remove();
		}else if($($('.textarea')[0].lastChild).hasClass('action'))
		{
			$($('.textarea')[0].lastChild).remove();
		}
		
		this.init();
	}
}
var calc = new calc;

$(function() {
	$('.number-btn'			).click(function(){calc.addNumber($(this).text());	})
	$('.percent-btn'		).click(function(){calc.addAction('%');				})
	$('.even-btn'			).click(function(){calc.answer();					})
	$('.point-btn'			).click(function(){calc.pointAction();				})
	$('.plusminus-btn'		).click(function(){calc.pmAction();					})
	$('.remove-btn'			).click(function(){calc.removeEl();					})
	$('.divid-btn'			).click(function(){calc.addAction('/');				})
	$('.multiplication-btn'	).click(function(){calc.addAction('*');				})
	$('.subtraction-btn'	).click(function(){calc.addAction('-');				})
	$('.plus-btn'			).click(function(){calc.addAction('+');				})
	$('.clear-btn'			).click(function(){calc.clear();					})
	
	$(document).keyup(function(event){
		switch(event.keyCode){
			case 97:
			case 49:{
				calc.addNumber(1);
			}break;
			case 50:
			case 98:{
				calc.addNumber(2);
			}break;
			case 51:
			case 99:{
				calc.addNumber(3);
			}break;
			case 52:
			case 100:{
				calc.addNumber(4);
			}break;
			case 53:
			case 101:{
				calc.addNumber(5);
			}break;
			case 54:
			case 102:{
				calc.addNumber(6);
			}break;
			case 55:
			case 103:{
				calc.addNumber(7);
			}break;
			case 56:
			case 104:{
				calc.addNumber(8);
			}break;
			case 57:
			case 105:{
				calc.addNumber(9);
			}break;
			case 48:
			case 96:{
				calc.addNumber(0);
			}break;
			case 187:
			case 107:{
				calc.addAction('+');
			}break;
			case 189:
			case 109:{
				calc.addAction('-');
			}break;
			case 220:
			case 111:
			case 191:{
				calc.addAction('/');
			}break;
			case 106:{
				calc.addAction('*');
			}break;
			case 67:{
				calc.clear();
			}break;
			case 13:{
				calc.answer();
			}break;
			case 8:{
				calc.removeEl();
			}break;
			case 110:{
				calc.pointAction();
			}break;
		}
	})

});